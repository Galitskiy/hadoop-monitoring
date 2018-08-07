#! /usr/bin/env python

'''
Author: Oleh Halytskyi
Date created: 8/6/2018
Date last modified: 8/6/2018
Python Version: 2.7
Home page: https://github.com/Galitskiy/hadoop-monitoring

Hadoop metrics:
- num_live_data_nodes
Number of live data nodes. Check will be triggered when value of this metric will be less than defined 'critical' threshold.

- dfs_used_percent
DFS usage in percent. Check will be triggered when value of this metric will be more than defined 'warning' or 'critical' threshold.

- block_pool_used_percent
Block pool usage in percent for each data node. Check will be triggered when value of this metric will be more than defined 'warning' or 'critical' threshold.

- hdfs_balancing
Check that no datanode is beyond the balancing threshold (in both ways).
The values of the output are the variation between the average disk usage of the nodes over the cluster and the disk usage of the current node on the cluster.
A negative value means that the node usage under the average disk usage of the datanodes over the cluster. A positive value means that it's over the average.
Check will be triggered if the datanode usage differs from average usage to more than 'warning' or 'critical' threshold.
'''

import sys
import requests
import argparse
import json

available_metrics = ['num_live_data_nodes', 'dfs_used_percent', 'block_pool_used_percent', 'hdfs_balancing']
state_ok=0
state_warning=1
state_critical=2

parser = argparse.ArgumentParser(description='Parameters for Hadoop Check')
parser.add_argument('-n', '--namenode', action="store", dest='namenode', type=str, help='Hadoop DFSHealth Hostname')
parser.add_argument('-p', '--port', action="store", dest='port', default=50070, type=int, help='Hadoop DFSHealth Port')
parser.add_argument('-w', '--warning', action="store", dest='warning', default=10, type=int, help='Warning threshold for DFS Usage')
parser.add_argument('-c', '--critical', action="store", dest='critical', default=15, type=int, help='Critical threshold for DFS Usage')
parser.add_argument('-m', '--metric', action="store", dest='metric', type=str, help='Metric name')
args = parser.parse_args()

if args.namenode == None:
    print "DFSHealth hostname not defined"
    sys.exit(state_critical)
elif args.metric == None:
    print "Metric name not defined"
    sys.exit(state_critical)
elif args.metric not in available_metrics:
    print "Incorrect metric: '%s'" % args.metric
    sys.exit(state_critical)

namenode = args.namenode
port = args.port
warning = args.warning
critical = args.critical
metric = args.metric

def get_data(qry):
    url = 'http://%s:%s/jmx?qry=%s' % (namenode, port, qry)
    try:
        r = requests.get(url=url)
        return r
    except:
        print "Can't connect to Hadoop DFSHealth"
        sys.exit(state_critical)

def check_metric_value():
    if metric == "num_live_data_nodes":
        r = get_data('Hadoop:service=NameNode,name=FSNamesystem')
        metric_value = r.json()['beans'][0]['NumLiveDataNodes']
        if metric_value >= critical:
            print "OK: Num Live Data Nodes: %s" % metric_value
            sys.exit(state_ok)
        else:
            print "CRITICAL: Num Live Data Nodes less than expected: %s" % metric_value
            sys.exit(state_critical)
    elif metric == "dfs_used_percent":
        r = get_data('Hadoop:service=NameNode,name=NameNodeInfo')
        metric_value = round(r.json()['beans'][0]['PercentUsed'], 2)
        if metric_value < critical and metric_value < warning:
            print "OK: DFS Used: %s%%" % metric_value
            sys.exit(state_ok)
        else:
            if metric_value >= critical:
                print "CRITICAL: DFS Used: %s%%" % metric_value
                sys.exit(state_critical)
            else:
                print "WARNING: DFS Used: %s%%" % metric_value
                sys.exit(state_warning)
    elif metric == "block_pool_used_percent" or metric == "hdfs_balancing":
        r = get_data('Hadoop:service=NameNode,name=NameNodeInfo')
        livenodes = json.loads(r.json()['beans'][0]['LiveNodes'])
        if len(livenodes) == 0:
            print "CRITICAL: Unable to find any node"
            sys.exit(state_critical)
        if metric == "hdfs_balancing":
            sum_values = 0
            for value in livenodes:
                sum_values += livenodes[value]['blockPoolUsedPercent']
            avg = sum_values / len(livenodes)
        livenodes_ok = ""
        livenodes_w = ""
        livenodes_c = ""
        for livenode in sorted(livenodes.iterkeys()):
            metric_value = livenodes[livenode]['blockPoolUsedPercent']
            if metric == "hdfs_balancing":
                metric_value = metric_value - avg
            metric_value = round(metric_value, 2)
            if abs(metric_value) >= critical:
                livenodes_c += "%s=%s%%, " % (livenode.split(':')[0], metric_value)
            elif abs(metric_value) >= warning:
                livenodes_w += "%s=%s%%, " % (livenode.split(':')[0], metric_value)
            else:
                livenodes_ok += "%s=%s%%, " % (livenode.split(':')[0], metric_value)
        if len(livenodes_c) > 0:
            print "CRITICAL: %s" % livenodes_c[:-2]
            sys.exit(state_critical)
        elif len(livenodes_w) > 0:
            print "WARNING: %s" % livenodes_w[:-2]
            sys.exit(state_warning)
        else:
            print "OK: %s" % livenodes_ok[:-2]
            sys.exit(state_ok)
    else:
        print "Can't check metric value"
        sys.exit(state_critical)


if __name__ == '__main__':
    check_metric_value()
