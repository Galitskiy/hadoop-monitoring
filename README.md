# hadoop-monitoring
Scripts for Hadoop monitoring

### *"[check_hadoop.py](check_hadoop.py)"* script support next metrics:
- num_live_data_nodes<br>
Number of live data nodes. Check will be triggered when value of this metric will be less than defined 'critical' threshold.

- dfs_used_percent<br>
DFS usage in percent. Check will be triggered when value of this metric will be more than defined 'warning' or 'critical' threshold.

- block_pool_used_percent<br>
Block pool usage in percent for each data node. Check will be triggered when value of this metric will be more than defined 'warning' or 'critical' threshold.

- hdfs_balancing<br>
Check that no datanode is beyond the balancing threshold (in both ways).<br>
The values of the output are the variation between the average disk usage of the nodes over the cluster and the disk usage of the current node on the cluster.<br>
A negative value means that the node usage under the average disk usage of the datanodes over the cluster. A positive value means that it's over the average.<br>
Check will be triggered if the datanode usage differs from average usage to more than 'warning' or 'critical' threshold.

### Examples of run
Check number of live data nodes
```
$ ./check_hadoop.py -n hbase-master01 -m num_live_data_nodes -c 7
OK: Num Live Data Nodes: 7
```

Check DFS usage in percent
```
$ ./check_hadoop.py -n hbase-master01 -m dfs_used_percent -w 80 -c 90
OK: DFS Used: 0.0%
```

Check block pool usage in percent for each data node
```
$ ./check_hadoop.py -n hbase-master01 -m block_pool_used_percent -w 80 -c 90
OK: hbase-region01=0.0%, hbase-region02=0.0%, hbase-region03=0.0%, hbase-region04=0.0%, hbase-region05=0.0%, hbase-region06=0.0%, hbase-region07=0.0%
```

Check HDFS balancing
```
./check_hadoop.py -n hbase-master01 -m hdfs_balancing -w 10 -c 15
OK: hbase-region01=0.0%, hbase-region02=0.0%, hbase-region03=-0.0%, hbase-region04=-0.0%, hbase-region05=-0.0%, hbase-region06=-0.0%, hbase-region07=0.0%
```
