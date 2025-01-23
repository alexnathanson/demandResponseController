#!/bin/bash

#run with:
#sudo /bin/bash start.sh

echo "Waiting 60 seconds..."

sleep 60

echo "Done waiting... activating venv"

#replace 'alex' with your user 

cd /home/alex/demandResponseController

source .venv/bin/activate

echo "Starting Demand Response Controller Experiment"

echo "view additional error logs at demandResponseController/experiment/runner.log"
python /home/alex/demandResponseController/experiment/powerstation_experiment1.py  > /home/alex/demandResponseController/experiment/runner.log 2>&1 &
