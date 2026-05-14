--------------------------- MODULE Shopping_List ---------------------------
EXTENDS Integers, FiniteSets

CONSTANTS
    POSSIBLE_REPLICA_IDs,
    POSSIBLE_USER_IDs,
    ASSIGNED_REPLICA,
    
    POSSIBLE_ITEM_IDs,
    POSSIBLE_ITEM_QUANTITIES,   \* quantities by which a user can change the quantity of an item
    
    NO_ITEM     \* placeholder for item ids that are not yet added to the list
    
VARIABLES
    replicas, action_counter
    
\* ----------------------------
\* Records
\* ----------------------------

Item ==
    [id                     : POSSIBLE_ITEM_IDs,
     added_quantities       : [POSSIBLE_USER_IDs -> Nat],
     removed_quantities     : [POSSIBLE_USER_IDs -> Nat],
     deleted_counter        : Nat  ] \* deleted is causal length counter
     
Replica ==
    [id     : POSSIBLE_REPLICA_IDs,
     recorded_items : [POSSIBLE_ITEM_IDs -> (Item \cup {NO_ITEM})]  ]
     

\* ----------------------------
\* Initialization
\* ----------------------------

Init == 
    /\ replicas = 
            [rid \in POSSIBLE_REPLICA_IDs |->
                [id |-> rid,
                 recorded_items |-> [iid \in POSSIBLE_ITEM_IDs |-> NO_ITEM]
                ]
            ]
    /\ action_counter = 0
    
    
\* ----------------------------
\* Helper Functions
\* ----------------------------

Is_deleted(item) ==
    item.deleted_counter % 2 = 1
    

Sum(f, S) ==
    LET RECURSIVE IterSum(_)
        IterSum(subS) == IF subS = {} THEN 0
                         ELSE LET x == CHOOSE x \in subS: TRUE
                              IN f[x] + IterSum(subS \ {x})
    IN IterSum(S)

Get_quantity(item_id, replica) ==
    LET item == replica.recorded_items[item_id]
    IN IF item = NO_ITEM THEN 0
       ELSE 
         LET total_added   == Sum(item.added_quantities, POSSIBLE_USER_IDs)
             total_removed == Sum(item.removed_quantities, POSSIBLE_USER_IDs)
             raw_quantity  == total_added - total_removed
         IN 
            \* Return 0 if the subtraction results in a negative number
            IF raw_quantity < 0 THEN 0 ELSE raw_quantity
            
            
\* ----------------------------
\* Item actions
\* ----------------------------

Add_item ==
    \E iid \in POSSIBLE_ITEM_IDs :
    \E rid \in POSSIBLE_REPLICA_IDs :
    \E actor \in POSSIBLE_USER_IDs :
    \E quantity \in POSSIBLE_ITEM_QUANTITIES :
        /\ ASSIGNED_REPLICA[actor] = rid
        /\ \A other_rid \in POSSIBLE_REPLICA_IDs : replicas[other_rid].recorded_items[iid] = NO_ITEM
        
        /\ LET new_item ==
                [ id |-> iid,
                  added_quantities |-> [uid \in POSSIBLE_USER_IDs |-> IF uid = actor THEN quantity ELSE 0],
                  removed_quantities |-> [uid \in POSSIBLE_USER_IDs |-> 0],
                  deleted_counter |-> 0
                ]
              new_replica ==
                [ replicas[rid] EXCEPT !.recorded_items = [@ EXCEPT ![iid] = new_item]]
           IN
                /\ replicas' = [replicas EXCEPT ![rid] = new_replica]
                /\ action_counter' = action_counter + 1
                
                
Increase_quantity ==
    \E iid \in POSSIBLE_ITEM_IDs :
    \E rid \in POSSIBLE_REPLICA_IDs :
    \E actor \in POSSIBLE_USER_IDs :
    \E quantity \in POSSIBLE_ITEM_QUANTITIES :
        /\ ASSIGNED_REPLICA[actor] = rid
        /\ replicas[rid].recorded_items[iid] # NO_ITEM
        
        /\ replicas' = [replicas EXCEPT ![rid].recorded_items[iid].added_quantities[actor] = @ + quantity]
        /\ action_counter' = action_counter + 1  
        

Decrease_quantity ==
    \E iid \in POSSIBLE_ITEM_IDs :
    \E rid \in POSSIBLE_REPLICA_IDs :
    \E actor \in POSSIBLE_USER_IDs :
    \E quantity \in POSSIBLE_ITEM_QUANTITIES :
        /\ ASSIGNED_REPLICA[actor] = rid
        /\ replicas[rid].recorded_items[iid] # NO_ITEM
        
        /\ replicas' = [replicas EXCEPT ![rid].recorded_items[iid].removed_quantities[actor] = @ + quantity]
        /\ action_counter' = action_counter + 1          
                
                
Delete_item ==
    \E iid \in POSSIBLE_ITEM_IDs :
    \E rid \in POSSIBLE_REPLICA_IDs :
    \E actor \in POSSIBLE_USER_IDs :
        /\ ASSIGNED_REPLICA[actor] = rid
        /\ replicas[rid].recorded_items[iid] # NO_ITEM
        /\ ~Is_deleted(replicas[rid].recorded_items[iid])
        
        /\ replicas' = [replicas EXCEPT ![rid].recorded_items[iid].deleted_counter = @ + 1]
        /\ action_counter' = action_counter + 1
        
        
Reinstate_item ==
    \E iid \in POSSIBLE_ITEM_IDs :
    \E rid \in POSSIBLE_REPLICA_IDs :
    \E actor \in POSSIBLE_USER_IDs :
        /\ ASSIGNED_REPLICA[actor] = rid
        /\ replicas[rid].recorded_items[iid] # NO_ITEM
        /\ Is_deleted(replicas[rid].recorded_items[iid])
        
        /\ replicas' = [replicas EXCEPT ![rid].recorded_items[iid].deleted_counter = @ + 1]
        /\ action_counter' = action_counter + 1
            

\* ----------------------------
\* Merge helper
\* ----------------------------

Merge_item(item_own, item_other) ==
    IF item_own = NO_ITEM /\ item_other = NO_ITEM
    THEN NO_ITEM
    ELSE IF item_own # NO_ITEM /\ item_other = NO_ITEM
    THEN item_own
    ELSE IF item_own = NO_ITEM /\ item_other # NO_ITEM
    THEN item_other
    ELSE
        LET 
            merged_added == [ u \in POSSIBLE_USER_IDs |-> 
                            CHOOSE n \in {item_own.added_quantities[u], item_other.added_quantities[u]} :
                                       n >= item_own.added_quantities[u] /\ n >= item_other.added_quantities[u] ]
            
            merged_removed == [ u \in POSSIBLE_USER_IDs |-> 
                            CHOOSE n \in {item_own.removed_quantities[u], item_other.removed_quantities[u]} :
                                       n >= item_own.removed_quantities[u] /\ n >= item_other.removed_quantities[u] ]
            
            merged_deleted == CHOOSE n \in {item_own.deleted_counter, item_other.deleted_counter} :
                                        n >= item_own.deleted_counter /\ n >= item_other.deleted_counter
        IN
            [ item_own EXCEPT !.added_quantities = merged_added,
                              !.removed_quantities = merged_removed,
                              !.deleted_counter = merged_deleted ]


\* ----------------------------
\* Merge action
\* ----------------------------

Merge_replicas ==
    \E own_rid, other_rid \in POSSIBLE_REPLICA_IDs :
        /\ own_rid /= other_rid
        /\ LET 
               own_items   == replicas[own_rid].recorded_items
               other_items == replicas[other_rid].recorded_items
               
               merged_recorded_items == [ iid \in POSSIBLE_ITEM_IDs |-> 
                   Merge_item(own_items[iid], other_items[iid]) ]
           IN
               /\ replicas' = [replicas EXCEPT ![own_rid].recorded_items = merged_recorded_items]
               /\ UNCHANGED action_counter


\* ----------------------------
\* Next action
\* ----------------------------

Next ==
    \/ Add_item
    \/ Increase_quantity
    \/ Decrease_quantity
    \/ Delete_item
    \/ Reinstate_item
    \/ Merge_replicas
    \/ UNCHANGED <<replicas, action_counter>>


\* ----------------------------
\* Invariants
\* ----------------------------

TypeOK ==
    \A rid \in POSSIBLE_REPLICA_IDs :
        /\ replicas[rid].recorded_items \in [POSSIBLE_ITEM_IDs -> (Item \cup {NO_ITEM}) ]
        
        
Quantities_non_negative ==
    \A rid \in POSSIBLE_REPLICA_IDs :
    \A iid \in POSSIBLE_ITEM_IDs :
        replicas[rid].recorded_items[iid] # NO_ITEM =>
            Get_quantity(iid, replicas[rid]) >= 0
            
            
\* ----------------------------
\* Safety Helpers
\* ----------------------------

\* The total added quantity for any user only increases or stays the same
No_decrease_added_quantities ==
    \A rid \in POSSIBLE_REPLICA_IDs, iid \in POSSIBLE_ITEM_IDs, u \in POSSIBLE_USER_IDs :
        (replicas[rid].recorded_items[iid] # NO_ITEM)
        =>
        /\ replicas'[rid].recorded_items[iid] # NO_ITEM
        /\ replicas'[rid].recorded_items[iid].added_quantities[u]
            >= replicas[rid].recorded_items[iid].added_quantities[u]

\* The total removed quantity for any user only increases or stays the same
No_decrease_removed_quantities ==
    \A rid \in POSSIBLE_REPLICA_IDs, iid \in POSSIBLE_ITEM_IDs, u \in POSSIBLE_USER_IDs :
        (replicas[rid].recorded_items[iid] # NO_ITEM)
        =>
        /\ replicas'[rid].recorded_items[iid] # NO_ITEM
        /\ replicas'[rid].recorded_items[iid].removed_quantities[u]
            >= replicas[rid].recorded_items[iid].removed_quantities[u]

\* The causal length counter for deletion/reinstate only increases
No_decrease_deleted_counter ==
    \A rid \in POSSIBLE_REPLICA_IDs, iid \in POSSIBLE_ITEM_IDs :
        (replicas[rid].recorded_items[iid] # NO_ITEM)
        =>
        /\ replicas'[rid].recorded_items[iid] # NO_ITEM
        /\ replicas'[rid].recorded_items[iid].deleted_counter
            >= replicas[rid].recorded_items[iid].deleted_counter
            

\* ----------------------------
\* Safety
\* ----------------------------
          
Safety_added_quantities_non_decreasing ==
    [] [ No_decrease_added_quantities ]_{<<replicas, action_counter>>}

Safety_removed_quantities_non_decreasing ==
    [] [ No_decrease_removed_quantities ]_{<<replicas, action_counter>>}

Safety_deleted_counter_non_decreasing ==
    [] [ No_decrease_deleted_counter ]_{<<replicas, action_counter>>}
    
    
\* ----------------------------
\* Liveness helpers
\* ----------------------------

All_replicas_have_at_least_added_quantity(iid, user, counter) ==
    \A rid \in POSSIBLE_REPLICA_IDs :
        /\ replicas[rid].recorded_items[iid] # NO_ITEM
        /\ replicas[rid].recorded_items[iid].added_quantities[user] >= counter

All_replicas_have_at_least_removed_quantity(iid, user, counter) ==
    \A rid \in POSSIBLE_REPLICA_IDs :
        /\ replicas[rid].recorded_items[iid] # NO_ITEM
        /\ replicas[rid].recorded_items[iid].removed_quantities[user] >= counter

All_replicas_have_at_least_deleted_counter(iid, counter) ==
    \A rid \in POSSIBLE_REPLICA_IDs :
        /\ replicas[rid].recorded_items[iid] # NO_ITEM
        /\ replicas[rid].recorded_items[iid].deleted_counter >= counter

All_replicas_have_item(iid) ==
    \A rid \in POSSIBLE_REPLICA_IDs : 
        replicas[rid].recorded_items[iid] # NO_ITEM


\* ----------------------------
\* Liveness
\* ----------------------------

\* 1. Always eventually all replicas need to agree on the quantities of each item
Liveness_Added_quantities_propagate ==
    \A rid \in POSSIBLE_REPLICA_IDs, iid \in POSSIBLE_ITEM_IDs, user \in POSSIBLE_USER_IDs :
        []<>(replicas[rid].recorded_items[iid] # NO_ITEM
            => All_replicas_have_at_least_added_quantity(iid, user, replicas[rid].recorded_items[iid].added_quantities[user]))

Liveness_Removed_quantities_propagate ==
    \A rid \in POSSIBLE_REPLICA_IDs, iid \in POSSIBLE_ITEM_IDs, user \in POSSIBLE_USER_IDs :
        []<>(replicas[rid].recorded_items[iid] # NO_ITEM
            => All_replicas_have_at_least_removed_quantity(iid, user, replicas[rid].recorded_items[iid].removed_quantities[user]))

\* 2. Always eventually all replicas need to agree if an item is present/removed
Liveness_Deletion_state_propagates ==
    \A rid \in POSSIBLE_REPLICA_IDs, iid \in POSSIBLE_ITEM_IDs :
        []<>(replicas[rid].recorded_items[iid] # NO_ITEM
            => All_replicas_have_at_least_deleted_counter(iid, replicas[rid].recorded_items[iid].deleted_counter))

\* 3. Every added item is eventually known by all replicas and remains known thereafter
Liveness_Item_presence_propagates ==
    \A rid \in POSSIBLE_REPLICA_IDs, iid \in POSSIBLE_ITEM_IDs :
        (replicas[rid].recorded_items[iid] # NO_ITEM)
            => <>[]All_replicas_have_item(iid)


\* ----------------------------
\* Specification
\* ----------------------------
Spec == Init /\ [][Next]_<<replicas, action_counter>>

FairSpec == 
    /\ Spec
    /\ WF_<<replicas, action_counter>>(Merge_replicas)


=============================================================================
\* Modification History
\* Last modified Thu May 14 13:08:35 CEST 2026 by floyd
\* Created Thu May 14 11:09:59 CEST 2026 by floyd
