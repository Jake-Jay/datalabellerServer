#!/bin/bash

echo 'Adding ten valid devices to the table'

Y=990000862401820

for ((X=0; X<10; X++ ));
do
 curl -vH "Content-Type: application/json" http://localhost:5000/api/register -X POST -d '{"device_number":"'$((Y+X))'"} '
done