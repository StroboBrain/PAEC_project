--------------------------- MODULE Shopping_List ---------------------------
EXTENDS Integers, FiniteSets

CONSTANTS
    POSSIBLE_REPLICA_IDs,
    POSSIBLE_USER_IDs,
    ASSIGNED_REPLICA,           \* Users only operate on one replica
    
    POSSIBLE_ITEM_IDs,
    POSSIBLE_ITEM_QUANTITIES,   \* quantities by which a user can change the quantity of an item
    POSSIBLE_REQUEST_IDs,       \* Requests to creater of item to change amount of item 
    
    NO_ITEM,                    \* placeholder for item ids that are not yet added to the list
    NO_REQUEST                  \* placeholder for request ids that are not yet added to the list
    
VARIABLES
    replicas, action_counter
    
\* ----------------------------
\* Records
\* ----------------------------

Item ==
    [id                     : POSSIBLE_ITEM_IDs,
     creator                : POSSIBLE_USER_IDs,
     quantity               : Nat,                  \* Quantity changes via request, only creator can accept/deny
     version                : Nat,                  \* Used only to track quantity of item
     deleted_counter        : Nat  ]                \* deleted is causal length counter
     
Request ==
    [id                     : POSSIBLE_REQUEST_IDs,
     sender                 : POSSIBLE_USER_IDs,
     change_amount          : Int,
     processed              : BOOLEAN  ]            \* Used to ensure a request is only processed once (-> double counting)
     
Replica ==
    [id                     : POSSIBLE_REPLICA_IDs,
     recorded_items         : [POSSIBLE_ITEM_IDs -> (Item \cup {NO_ITEM})],
     recorded_requests      : [POSSIBLE_REQUEST_IDs -> (Request \cup {NO_REQUEST})]  ]
     

\* ----------------------------
\* Initialization
\* ----------------------------

Init == 
    /\ replicas = 
            [rid \in POSSIBLE_REPLICA_IDs |->
                [id                 |-> rid,
                 recorded_items     |-> [iid \in POSSIBLE_ITEM_IDs |-> NO_ITEM],
                 recorded_requests  |-> [rqid \in POSSIBLE_REQUEST_IDs |-> NO_REQUEST]
                ]
            ]
    /\ action_counter = 0
    
    
\* ----------------------------
\* Helper Functions
\* ----------------------------

\* Causal length logic
Is_deleted(item) ==
    item.deleted_counter % 2 = 1
               
            
\* ----------------------------
\* Item actions
\* ----------------------------

Add_item ==
    \E iid \in POSSIBLE_ITEM_IDs :
    \E rid \in POSSIBLE_REPLICA_IDs :
    \E actor \in POSSIBLE_USER_IDs :
    \E item_quantity \in POSSIBLE_ITEM_QUANTITIES :
        /\ ASSIGNED_REPLICA[actor] = rid
        \* No other replica has item with same id (uniqueness, in real implementation use dynamic ids)
        /\ \A other_rid \in POSSIBLE_REPLICA_IDs : replicas[other_rid].recorded_items[iid] = NO_ITEM
        
        /\ LET new_item ==
                [ id |-> iid,
                  creator |-> actor,
                  quantity |-> item_quantity,
                  version |-> 1,
                  deleted_counter |-> 0
                ]
              new_replica ==
                [ replicas[rid] EXCEPT !.recorded_items = [@ EXCEPT ![iid] = new_item]]
           IN
                /\ replicas' = [replicas EXCEPT ![rid] = new_replica]
                /\ action_counter' = action_counter + 1
                
                
Request_quantity_increase ==
    \E iid \in POSSIBLE_ITEM_IDs :
    \E rid \in POSSIBLE_REPLICA_IDs :
    \E rrid \in POSSIBLE_REQUEST_IDs :
    \E actor \in POSSIBLE_USER_IDs :
    \E quantity \in POSSIBLE_ITEM_QUANTITIES :
        /\ ASSIGNED_REPLICA[actor] = rid
        /\ replicas[rid].recorded_items[iid] # NO_ITEM
        \* No other replica has request with same id (uniqueness, in real implementation use dynamic ids)
        /\ \A other_rid \in POSSIBLE_REPLICA_IDs : replicas[other_rid].recorded_requests[rrid] = NO_REQUEST
        
        /\ LET new_request ==
                    [ id |-> rrid,
                      sender |-> actor,
                      change_amount |-> quantity,
                      processed |-> FALSE
                    ]
                new_replica ==
                    [ replicas[rid] EXCEPT !.recorded_requests = [@ EXCEPT ![rrid] = new_request]]
           IN 
                /\ replicas' = [replicas EXCEPT ![rid] = new_replica]
                /\ action_counter' = action_counter + 1
                
                
Request_quantity_decrease ==
    \E iid \in POSSIBLE_ITEM_IDs :
    \E rid \in POSSIBLE_REPLICA_IDs :
    \E rrid \in POSSIBLE_REQUEST_IDs :
    \E actor \in POSSIBLE_USER_IDs :
    \E quantity \in POSSIBLE_ITEM_QUANTITIES :
        /\ ASSIGNED_REPLICA[actor] = rid
        /\ replicas[rid].recorded_items[iid] # NO_ITEM
        \* No other replica has request with same id (uniqueness, in real implementation use dynamic ids)
        /\ \A other_rid \in POSSIBLE_REPLICA_IDs : replicas[other_rid].recorded_requests[rrid] = NO_REQUEST
        
        /\ LET new_request ==
                    [ id |-> rrid,
                      sender |-> actor,
                      change_amount |-> quantity * (-1),
                      processed |-> FALSE
                    ]
                new_replica ==
                    [ replicas[rid] EXCEPT !.recorded_requests = [@ EXCEPT ![rrid] = new_request]]
           IN 
                /\ replicas' = [replicas EXCEPT ![rid] = new_replica]
                /\ action_counter' = action_counter + 1
                

\* Accept quantitiy change requst if quantity won't go negative                
Accept_request ==
    \E iid \in POSSIBLE_ITEM_IDs :
    \E rid \in POSSIBLE_REPLICA_IDs :
    \E rrid \in POSSIBLE_REQUEST_IDs :
    \E actor \in POSSIBLE_USER_IDs :
        /\ ASSIGNED_REPLICA[actor] = rid
        /\ replicas[rid].recorded_items[iid] # NO_ITEM
        /\ replicas[rid].recorded_items[iid].creator = actor
        /\ replicas[rid].recorded_requests[rrid] # NO_REQUEST
        /\ replicas[rid].recorded_requests[rrid].processed = FALSE
        
        /\ (replicas[rid].recorded_items[iid].quantity + replicas[rid].recorded_requests[rrid].change_amount) >= 0
        /\ LET 
               current_item == replicas[rid].recorded_items[iid]
               current_req  == replicas[rid].recorded_requests[rrid]

               new_item ==
                    [ current_item EXCEPT !.quantity = @ + current_req.change_amount,
                                          !.version = @ + 1]
               new_request ==
                    [ current_req EXCEPT !.processed = TRUE ]
               new_replica ==
                    [ replicas[rid] EXCEPT !.recorded_items[iid] = new_item,
                                           !.recorded_requests[rrid] = new_request ]
           IN 
                /\ replicas' = [replicas EXCEPT ![rid] = new_replica]
                /\ action_counter' = action_counter + 1
                

\* Deny quantity change request (for any reason)         
Deny_request ==
    \E iid \in POSSIBLE_ITEM_IDs :
    \E rid \in POSSIBLE_REPLICA_IDs :
    \E rrid \in POSSIBLE_REQUEST_IDs :
    \E actor \in POSSIBLE_USER_IDs :
        /\ ASSIGNED_REPLICA[actor] = rid
        /\ replicas[rid].recorded_items[iid] # NO_ITEM
        /\ replicas[rid].recorded_items[iid].creator = actor
        /\ replicas[rid].recorded_requests[rrid] # NO_REQUEST
        /\ replicas[rid].recorded_requests[rrid].processed = FALSE
        
        /\ LET 
               current_req  == replicas[rid].recorded_requests[rrid]
               
               new_request ==
                    [ current_req EXCEPT !.processed = TRUE ]
               new_replica ==
                    [ replicas[rid] EXCEPT !.recorded_requests[rrid] = new_request ]
           IN 
                /\ replicas' = [replicas EXCEPT ![rid] = new_replica]
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
    \* If only one replica has the item with id keep this one
    IF item_own = NO_ITEM /\ item_other = NO_ITEM
    THEN NO_ITEM
    ELSE IF item_own # NO_ITEM /\ item_other = NO_ITEM
    THEN item_own
    ELSE IF item_own = NO_ITEM /\ item_other # NO_ITEM
    THEN item_other
    \* If both replicas have item with id apply merge logic
    ELSE
        LET 
            \* Determine which record holds the most recent version for quantity
            higher_version_item == IF item_own.version >= item_other.version 
                                   THEN item_own 
                                   ELSE item_other
            
            \* Delete is concurrently updated independent of the version logic (use cls merge)
            merged_deleted == CHOOSE n \in {item_own.deleted_counter, item_other.deleted_counter} :
                                    n >= item_own.deleted_counter /\ n >= item_other.deleted_counter
        IN
            [ item_own EXCEPT !.quantity        = higher_version_item.quantity,
                              !.version         = higher_version_item.version,
                              !.deleted_counter = merged_deleted ]


Merge_request(req_own, req_other) ==
    IF req_own = NO_REQUEST /\ req_other = NO_REQUEST
    THEN NO_REQUEST
    ELSE IF req_own # NO_REQUEST /\ req_other = NO_REQUEST
    THEN req_own
    ELSE IF req_own = NO_ITEM /\ req_other # NO_REQUEST
    THEN req_other
    ELSE IF req_own = NO_REQUEST /\ req_other # NO_REQUEST
    THEN req_other
    ELSE  \* Prefer true in merges
        [ req_own EXCEPT !.processed = req_own.processed \/ req_other.processed ]

\* ----------------------------
\* Merge action
\* ----------------------------

Merge_replicas ==
    \E own_rid, other_rid \in POSSIBLE_REPLICA_IDs :
        /\ own_rid /= other_rid
        /\ LET 
               own_items    == replicas[own_rid].recorded_items
               other_items   == replicas[other_rid].recorded_items
               own_requests  == replicas[own_rid].recorded_requests
               other_requests == replicas[other_rid].recorded_requests
               
               merged_recorded_items == [ iid \in POSSIBLE_ITEM_IDs |-> 
                   Merge_item(own_items[iid], other_items[iid]) ]
               
               merged_recorded_requests == [ rrid \in POSSIBLE_REQUEST_IDs |-> 
                   Merge_request(own_requests[rrid], other_requests[rrid]) ]
           IN
               /\ replicas' = [replicas EXCEPT ![own_rid].recorded_items = merged_recorded_items,
                                              ![own_rid].recorded_requests = merged_recorded_requests]
               /\ UNCHANGED action_counter


\* ----------------------------
\* Next action
\* ----------------------------

Next ==
    \/ Add_item
    \/ Request_quantity_increase
    \/ Request_quantity_decrease
    \/ Deny_request
    \/ Accept_request
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
        /\ replicas[rid].recorded_requests \in [POSSIBLE_REQUEST_IDs -> (Request \cup {NO_REQUEST}) ]
        
        
Quantities_non_negative ==
    \A rid \in POSSIBLE_REPLICA_IDs :
    \A iid \in POSSIBLE_ITEM_IDs :
        replicas[rid].recorded_items[iid] # NO_ITEM =>
            replicas[rid].recorded_items[iid].quantity >= 0
            
            
\* ----------------------------
\* Safety Helpers
\* ----------------------------

\* The causal length counter for deletion/reinstate only increases
No_decrease_deleted_counter ==
    \A rid \in POSSIBLE_REPLICA_IDs, iid \in POSSIBLE_ITEM_IDs :
        (replicas[rid].recorded_items[iid] # NO_ITEM)
        =>
        /\ replicas'[rid].recorded_items[iid] # NO_ITEM
        /\ replicas'[rid].recorded_items[iid].deleted_counter
            >= replicas[rid].recorded_items[iid].deleted_counter
            
\* The version counter for items only increases
No_decrease_version_counter ==
    \A rid \in POSSIBLE_REPLICA_IDs, iid \in POSSIBLE_ITEM_IDs :
        (replicas[rid].recorded_items[iid] # NO_ITEM)
        =>
        /\ replicas'[rid].recorded_items[iid] # NO_ITEM
        /\ replicas'[rid].recorded_items[iid].version
            >= replicas[rid].recorded_items[iid].version
            
\* Processed requests stay processed
Processed_requests_terminal ==
    \A rid \in POSSIBLE_REPLICA_IDs, rrid \in POSSIBLE_REQUEST_IDs :
        (replicas[rid].recorded_requests[rrid] # NO_REQUEST /\ replicas[rid].recorded_requests[rrid].processed = TRUE)
        =>
        /\ replicas'[rid].recorded_requests[rrid] # NO_REQUEST
        /\ replicas'[rid].recorded_requests[rrid].processed = TRUE
            

\* ----------------------------
\* Additional Safety
\* ----------------------------

\* Monotinic growth of causal length counter
Safety_deleted_counter_non_decreasing ==
    [] [ No_decrease_deleted_counter ]_{<<replicas, action_counter>>}
    
\* Monotinic growth of version counter
Safety_version_counter_non_decreasing ==
    [] [ No_decrease_version_counter ]_{<<replicas, action_counter>>}   
    
\* Processed requests terminal
Safety_processed_requests_terminal ==
    [] [ Processed_requests_terminal ]_{<<replicas, action_counter>>}   
    
    
    
\* ----------------------------
\* Liveness helpers
\* ----------------------------

All_replicas_have_at_least_item_version(iid, version) ==
    \A rid \in POSSIBLE_REPLICA_IDs :
        /\ replicas[rid].recorded_items[iid] /= NO_ITEM
        /\ replicas[rid].recorded_items[iid].version >= version

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

\* 1. Always eventually all replicas need to catch up to the latest version of an item,
\*    so most recent quantity updates reach every replica
Liveness_versions_propagate ==
    \A rid \in POSSIBLE_REPLICA_IDs, iid \in POSSIBLE_ITEM_IDs :
        []<>(replicas[rid].recorded_items[iid] /= NO_ITEM
            => All_replicas_have_at_least_item_version(iid, replicas[rid].recorded_items[iid].version))

\* 2. Always eventually all replicas need to agree if an item is present/removed;
\*    This is independend from the version as we allow concurrent add/remove
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
\* Last modified Mon May 25 08:57:52 CEST 2026 by floyd
\* Created Thu May 14 11:09:59 CEST 2026 by floyd
