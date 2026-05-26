---- MODULE MC ----
EXTENDS Shopping_List, TLC

\* MV CONSTANT declarations@modelParameterConstants
CONSTANTS
iid1
----

\* MV CONSTANT declarations@modelParameterConstants
CONSTANTS
a, b, c
----

\* MV CONSTANT declarations@modelParameterConstants
CONSTANTS
rr1, rr2
----

\* MV CONSTANT declarations@modelParameterConstants
CONSTANTS
r1, r2, r3
----

\* MV CONSTANT definitions POSSIBLE_ITEM_IDs
const_17797754863562000 == 
{iid1}
----

\* MV CONSTANT definitions POSSIBLE_USER_IDs
const_17797754863563000 == 
{a, b, c}
----

\* MV CONSTANT definitions POSSIBLE_REQUEST_IDs
const_17797754863564000 == 
{rr1, rr2}
----

\* MV CONSTANT definitions POSSIBLE_REPLICA_IDs
const_17797754863565000 == 
{r1, r2, r3}
----

\* CONSTANT definitions @modelParameterConstants:5POSSIBLE_ITEM_QUANTITIES
const_17797754863566000 == 
1..2
----

\* CONSTANT definitions @modelParameterConstants:7ASSIGNED_REPLICA
const_17797754863567000 == 
[u \in POSSIBLE_USER_IDs |-> IF u = a THEN r1 ELSE IF u = b THEN r2 ELSE r3]
----

\* CONSTRAINT definition @modelParameterContraint:0
constr_17797754863568000 ==
action_counter <= 8
----
=============================================================================
\* Modification History
\* Created Tue May 26 08:04:46 CEST 2026 by floyd
