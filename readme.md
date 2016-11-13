# Undo-Redo Logging

**To run:** `python undoredologging.py`  

We implement the `log files` of the `Undo logging protocol` and the `Redo logging protocol` for three transactions:  
1. `code/T1`  
2. `code/T2`  
3. `code/T3`  
with the initial values of `A = 8, B = 8, C = 5, D = 10`  

We consider the above three transactions and assume a `round robin` method for processing these transactions - in the order of T1 first, then T2 second and T3 third, taking `time quantum` to be varying from 1 action to entire transaction (all actions of the transaction) at a time.  

**Eg. of a time quantum:** 2 steps of T1, 2 of T2, 2 of T3 and then next 2 steps of T2 and so on.  

There will be 9 such cases given these transactions (T2 is the longest with 9 actions) and hence 18 log files - one each of undo and redo for each of the 9 cases.  

For each log message, the logs also contain the `hard disk copies` of the variable values in each line of the message.  

The log messages are of four types:  
1. \<START TNUM\>  
2. <TNUM, varName, oldvalifundo/newvalifredo>  
3. <COMMIT TNUM>  

Care has also been taken to flush the logs from the buffers at appropriate times.  

The `correctness principle` holds only in the 7th, 8th and 9th time quantum cases as indicated by the presence of an integer - the time quantum number - at the end of both of the undo and redo log files of the time quantums 7, 8, 9. In other cases, the value of the variables given each of the transactions executed completely, one after the other, doesn't match the value of the variables given the execution of the transactions in that time quantum.  

