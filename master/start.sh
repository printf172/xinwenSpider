#!/bin/bash

while :
do
	ls
	while :
	do
        echo "--------------------------------------------------"
		echo "Please enter s, k or ex command."
		echo "s: Start spider."
		echo "k: Kill spider."
        echo "ex: Exit to the upper layer. eg:'ex'"
		read -p ": " op
        if [[ $op = ex ]] || [[ $op = exit ]]; then
			exit 
		fi
		if [[ $op =~ ^s ]] ;then
			ARR=($op)
			nohup python3 ${ARR[1]} >/dev/null 2>&1 &
			continue
		fi
        if [[ $op =~ ^k ]] ;then
			ARR=($op)
			ps -ef|grep ${ARR[1]} |awk '{print $2}'|xargs kill -9
			continue
		fi
		echo "Wronging command!"
	done
done