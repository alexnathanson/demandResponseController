#!/bin/bash

#run with:
#sudo /bin/bash start.sh

echo "Waiting 60 seconds..."

sleep 60

echo "Done waiting... activating venv"

#replace 'alex' with your user name
source /home/alex/demandResponseController/.venv/bin/activate

echo "Starting Demand Response Controller Experiment"

echo "view error logs at demandResponseController/runner.log"
python /home/alex/demandResponseController/experiment/powerstation_experiment1.py  > /home/alex/demandResponseController/experiment/runner.log 2>&1 &
