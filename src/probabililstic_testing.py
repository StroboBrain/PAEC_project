from collections import defaultdict
import random
import pprint
from typing import Tuple, List
import time
import argparse

from item_handler import Item, ItemHandler
from request_handler import Request, RequestHandler
from replica_sync import ReplicaSync
from storage_provider import get_backend, use_memory_backend

# --- Configuration Constants ---
NUM_USERS = 5
MAX_STEPS = 1000
MAX_TEST_RUNS = 5

backend = None
users = []
action_counter = defaultdict(lambda: {"Passed": 0, "Failed": 0})

# TLA actions to test
ACTIONS = [
    "create_item",
    "create_request",
    "process_request_accept",
    "process_request_deny",
    "delete_item",
    "reinstate_item"
]

def _setup():
    """Initializes the completely isolated memory backend environment."""
    global users, backend
    use_memory_backend()
    backend = get_backend()
    users = []
    clear_replicas(users)

def clear_replicas(users_list: list):
    all_user_ids = [f"user{i}" for i in range(NUM_USERS)]
    for i in range(NUM_USERS):
        user_id = f"user{i}"
        users_list.append(user_id)
        replica = {
            "id": user_id,
            "recorded_items": {},
            "recorded_requests": {},
            "known_users": {uid: uid for uid in all_user_ids}
        }
        backend.write_full_replica(user_id, replica)

# ==========================================
#        TLA+ SAFETY / INVARIANTS
# ==========================================

def invariant_non_negative_quantities(replica: dict) -> Tuple[bool, str]:
    items = replica.get("recorded_items", {}) or {}
    for iid, item in items.items():
        if not item:
            continue
        qty = item.get("quantity", 0)
        if qty < 0:
            return False, f"Item {iid} ('{item.get('name')}') broke non-negative rule: quantity={qty}"
    return True, ""


def check_invariants(replica: dict) -> Tuple[bool, List[str]]:
    checks = [
        invariant_non_negative_quantities,
    ]
    errors = []
    for check in checks:
        ok, msg = check(replica)
        if not ok:
            errors.append(msg)
    return (len(errors) == 0), errors

# ==========================================
#        TLA+ Temporal Safety Properties
# ==========================================

def temporal_monotonically_growing_item_versions(old_state: dict, new_state: dict) -> Tuple[bool, str]:
    old_items = old_state.get("recorded_items", {}) or {}
    new_items = new_state.get("recorded_items", {}) or {}
    
    for iid, old_item in old_items.items():
        new_item = new_items.get(iid)
        if not new_item:
            return False, f"Item {iid} was entirely deleted from the state instead of tracking tombstone"
        
        if new_item.get("version", 0) < old_item.get("version", 0):
            return False, f"Item {iid} version decreased: {old_item['version']} -> {new_item['version']}"
    return True, ""

def temporal_monotonically_growing_deletion_counters(old_state: dict, new_state: dict) -> Tuple[bool, str]:
    old_items = old_state.get("recorded_items", {}) or {}
    new_items = new_state.get("recorded_items", {}) or {}
    
    for iid, old_item in old_items.items():
        new_item = new_items.get(iid)
        if new_item and new_item.get("deleted_counter", 0) < old_item.get("deleted_counter", 0):
            return False, f"Item {iid} deleted_counter decreased: {old_item['deleted_counter']} -> {new_item['deleted_counter']}"
    return True, ""

def temporal_processed_requests_are_terminal(old_state: dict, new_state: dict) -> Tuple[bool, str]:
    old_reqs = old_state.get("recorded_requests", {}) or {}
    new_reqs = new_state.get("recorded_requests", {}) or {}
    
    for rrid, old_req in old_reqs.items():
        new_req = new_reqs.get(rrid)
        if new_req and old_req.get("processed", False) and not new_req.get("processed", False):
            return False, f"Request {rrid} reverted from processed status back to pending"
    return True, ""

def check_temporal_properties(old_state: dict, new_state: dict) -> Tuple[bool, List[str]]:
    checks = [
        temporal_monotonically_growing_item_versions,
        temporal_monotonically_growing_deletion_counters,
        temporal_processed_requests_are_terminal
    ]
    errors = []
    for check in checks:
        ok, msg = check(old_state, new_state)
        if not ok:
            errors.append(msg)
    return (len(errors) == 0), errors

# ==========================================
#         LIVENESS CONVERGENCE TESTS
# ==========================================

def do_final_merges():
    """All replicas merge together -> after this all replcias should be the same.
       Together with the safety properties, this should ensure the Liveness properties aswell."""
    if not users:
        return
    user0 = users[0]
    
    # All users merge their local states directly into user0
    ReplicaSync.user_id = user0
    for user in users[1:]:
        to_merge_replica = backend.get_full_replica(user)
        if to_merge_replica:
            ReplicaSync._merge_replica(to_merge_replica)

    # user0 distributes full view to all other users
    user0_replica = backend.get_full_replica(user0)
    for user in users[1:]:
        ReplicaSync.user_id = user
        ReplicaSync._merge_replica(user0_replica)

def diff_replicas(rep_a: dict, rep_b: dict, node_a: str, node_b: str) -> str:
    """Computes a clean, targeted diff showing exactly what field drifted between two replicas."""
    diff_lines = [f"\n--- State Drift Detected between {node_a} and {node_b} ---"]
    
    categories = ["recorded_items", "recorded_requests", "known_users"]
    for cat in categories:
        dict_a = rep_a.get(cat, {}) or {}
        dict_b = rep_b.get(cat, {}) or {}
        
        if dict_a == dict_b:
            continue
            
        diff_lines.append(f"  [{cat} differences]:")
        all_keys = set(dict_a.keys()) | set(dict_b.keys())
        
        for key in all_keys:
            if key not in dict_a:
                diff_lines.append(f"    - ID '{key}' missing on {node_a}, present on {node_b}: {dict_b[key]}")
            elif key not in dict_b:
                diff_lines.append(f"    - ID '{key}' present on {node_a}, missing on {node_b}: {dict_a[key]}")
            elif dict_a[key] != dict_b[key]:
                # The record exists in both, but fields inside differ
                val_a = dict_a[key]
                val_b = dict_b[key]
                
                if isinstance(val_a, dict) and isinstance(val_b, dict):
                    field_diffs = []
                    all_fields = set(val_a.keys()) | set(val_b.keys())
                    for field in all_fields:
                        if val_a.get(field) != val_b.get(field):
                            field_diffs.append(f"'{field}': {val_a.get(field)} vs {val_b.get(field)}")
                    diff_lines.append(f"    - ID '{key}' properties mismatched -> {', '.join(field_diffs)}")
                else:
                    diff_lines.append(f"    - ID '{key}' values mismatched -> {node_a}: {val_a} vs {node_b}: {val_b}")
                    
    return "\n".join(diff_lines)


def check_all_replicas_the_same() -> Tuple[bool, str]:
    """Checks for Strong Eventual Consistency across all replicas."""
    if not users:
        return True, ""
    
    first = backend.get_full_replica(users[0]).copy()
    first.pop("id", None)  # Remove the unique node ID field from the comparison
    
    for u in users[1:]:
        replica = backend.get_full_replica(u).copy()
        replica.pop("id", None)  # Remove this node's unique ID field as well
        
        if replica != first:
            # Generate and print just the targeted difference trace
            drift_report = diff_replicas(first, replica, users[0], u)
            print(drift_report)
            return False, f"Node '{users[0]}' replica state has drifted from Node '{u}'"
            
    return True, ""

# ==========================================
#          RANDOM ACTIONS
# ==========================================

def create_item_action(rdm, actor):
    name = f"item_{rdm.randint(1, 100)}"
    qty = rdm.randint(1, 20)
    status, _ = ItemHandler.create_item(actor, name, qty)
    return status

def create_request_action(rdm, actor):
    replica = backend.get_full_replica(actor) or {}
    items = replica.get("recorded_items", {}) or {}
    if not items:
        return 0
    else:
        iid = rdm.choice(list(items.keys()))
        item_name = items[iid].get("name", "Unknown")
    change = rdm.randint(-5, 20)
    name = f"req_{rdm.randint(1000, 9999)}"
    
    status, _ = RequestHandler.create_request(actor, iid, item_name, name, change)
    return status

def process_request_accept_action(rdm, actor):
    replica = backend.get_full_replica(actor) or {}
    reqs = replica.get("recorded_requests", {}) or {}
    pending = [rrid for rrid, _ in reqs.items()]
    if not pending:
        return 0
    
    rrid = rdm.choice(pending)
    status, _ = RequestHandler.process_request(actor, rrid, accept=False)
    return status

def process_request_deny_action(rdm, actor):
    replica = backend.get_full_replica(actor) or {}
    reqs = replica.get("recorded_requests", {}) or {}
    pending = [rrid for rrid, _ in reqs.items()]
    if not pending:
        return 0
    
    rrid = rdm.choice(pending)
    status, _ = RequestHandler.process_request(actor, rrid, accept=False)
    return status

def delete_item_action(rdm, actor):
    replica = backend.get_full_replica(actor) or {}
    items = replica.get("recorded_items", {}) or {}
    iids = [iid for iid, _ in items.items()]
    if not iids:
        return 0
    
    iid = rdm.choice(iids)
    status, _ = ItemHandler.delete_item(actor, iid)
    return status

def reinstate_item_action(rdm, actor):
    replica = backend.get_full_replica(actor) or {}
    items = replica.get("recorded_items", {}) or {}
    iids = [iid for iid, _ in items.items()]
    if not iids:
        return 0
    
    iid = rdm.choice(iids)
    status, _ = ItemHandler.reinstate_item(actor, iid)

    return status

def merge_action(user1, user2):
    ReplicaSync.user_id = user1
    user2_replica = backend.get_full_replica(user2)
    if user2_replica:
        ReplicaSync._merge_replica(user2_replica)

ACTION_MAP = {
    "create_item": create_item_action,
    "create_request": create_request_action,
    "process_request_accept": process_request_accept_action,
    "process_request_deny": process_request_deny_action,
    "delete_item": delete_item_action,
    "reinstate_item": reinstate_item_action
}

# ==========================================
#            MAIN TEST LOOP
# ==========================================

def run_test(seed: int, do_temporal_checks=True):
    global users
    rdm = random.Random(seed)

    for step in range(MAX_STEPS):
        # High Probability Merge Action (25% chance per step)
        if rdm.randint(0, 99) < 25 and len(users) > 1:
            user1, user2 = rdm.sample(users, 2)
            action_name = "merge"
            affected_users = [user1, user2]
            
            if do_temporal_checks:
                old_state = {uid: backend.get_full_replica(uid) for uid in affected_users}
            
            merge_action(user1, user2)
            action_counter[action_name]["Passed"] += 1
        else:
            action_name = rdm.choice(ACTIONS)
            actor = rdm.choice(users)
            affected_users = [actor]
            
            if do_temporal_checks:
                old_state = {actor: backend.get_full_replica_deep(actor)}

            status = ACTION_MAP[action_name](rdm, actor)

            if status == 1 or (isinstance(status, str) and len(status) == 36 and status.count('-') == 4):
                action_counter[action_name]["Passed"] += 1
            elif status == -1:
                action_counter[action_name]["Failed"] += 1
            else:
                continue

        # Verifying correctness properties
        new_state = {uid: backend.get_full_replica(uid) for uid in affected_users}
        for uid in affected_users:
            # 1. Invariant Safety Check
            ok, errs = check_invariants(new_state[uid])
            if not ok:
                print(f"\n[CRITICAL FAILURE] Safety Invariant Broken on Node '{uid}' at Step {step} during '{action_name}'")
                print(f"Errors Identified: {errs}")
                print("State Dump:")
                pprint.pprint(new_state[uid])
                return False
            
            # 2. Two-State Temporal Safety Check
            if do_temporal_checks and old_state.get(uid):
                ok, errs = check_temporal_properties(old_state[uid], new_state[uid])
                if not ok:
                    print(f"\n[CRITICAL FAILURE] Temporal Progression Violated on Node '{uid}' at Step {step} during '{action_name}'")
                    print(f"Errors Identified: {errs}")
                    print("Old State Instance Snapshot:")
                    pprint.pprint(old_state[uid])
                    print("New State Instance Snapshot:")
                    pprint.pprint(new_state[uid])
                    return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=MAX_STEPS)
    parser.add_argument("--runs", type=int, default=MAX_TEST_RUNS)
    args = parser.parse_args()

    MAX_STEPS = args.steps
    MAX_TEST_RUNS = args.runs

    print("=" * 75)
    print(f"STARTING SIMULATION RUN: {MAX_TEST_RUNS} seeds, {MAX_STEPS} operations per scenario loop step")
    print("=" * 75)

    start_time = time.time()
    successful_runs = 0

    for run_idx in range(1, MAX_TEST_RUNS + 1):
        current_seed = random.randint(100000, 999999)
        _setup()

        status_msg = f"Running scenario batch {run_idx}/{MAX_TEST_RUNS} (Seed Vector: {current_seed})..."
        print(f"\r{status_msg}", end="", flush=True)

        passed = run_test(seed=current_seed, do_temporal_checks=True)
        
        if not passed:
            print(f"\n[FAILURE] Run {run_idx} broke invariant constraints at seed {current_seed}")
            break
            
        # Liveness verification  at the end of each run
        do_final_merges()
        converged, merge_error_msg = check_all_replicas_the_same()
        
        if not converged:
            print(f"\n[FAILURE] Run {run_idx} failed liveness convergence checks.")
            print(merge_error_msg)
            break
            
        successful_runs += 1

    total_time = time.time() - start_time
    avg_time = total_time / successful_runs if successful_runs > 0 else 0.0


    total_items_generated = 0
    total_requests_generated = 0
    if users:
        sample_replica = backend.get_full_replica(users[0]) or {}
        total_items_generated = len(sample_replica.get("recorded_items", {}))
        total_requests_generated = len(sample_replica.get("recorded_requests", {}))

    report_output = []
    report_output.append("=" * 75)
    report_output.append("                          FINAL SIMULATION REPORT")
    report_output.append("=" * 75)
    report_output.append(f"Execution Status:     {'SUCCESS' if successful_runs == MAX_TEST_RUNS else 'CRITICAL FAILURE'}")
    report_output.append(f"Runs Completed:       {successful_runs} / {MAX_TEST_RUNS}")
    report_output.append(f"Steps per run:        {MAX_STEPS}")
    report_output.append(f"Total Elapsed Time:   {total_time:.3f} seconds")
    report_output.append(f"Average Run Time:     {avg_time:.3f} seconds/run")
    report_output.append(f"Final Retained Items: {total_items_generated}")
    report_output.append(f"Final Requests Sent:  {total_requests_generated}")
    report_output.append("-" * 75)
    report_output.append(f"{'Action Name':<28} | {'Passed':<12} | {'Failed':<12} | {'Success Rate':<12}")
    report_output.append("-" * 75)

    all_actions = sorted(list(action_counter.keys()))
    if "merge" not in all_actions and action_counter.get("merge", {}).get("Passed", 0) > 0:
        all_actions.append("merge")

    for act in all_actions:
        counters = action_counter.get(act, {"Passed": 0, "Failed": 0})
        passed_val = counters["Passed"]
        failed_val = counters["Failed"]
        total_val = passed_val + failed_val
        
        rate_str = f"{(passed_val / total_val * 100):.1f}%" if total_val > 0 else "0.0%"
        report_output.append(f"{act:<28} | {passed_val:<12} | {failed_val:<12} | {rate_str:<12}")
        
    report_output.append("=" * 75)

    final_report_string = "\n".join(report_output)
    print(final_report_string)

    file_seed = random.randint(1000, 9999999)
    filename = f"probabilistic_results_runs{MAX_TEST_RUNS}_steps{MAX_STEPS}_{file_seed}.txt"

    with open(filename, "w") as out_file:
        out_file.write(final_report_string)
        
    print(f"Results saved to: {filename}")