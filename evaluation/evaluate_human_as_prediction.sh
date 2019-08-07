NLG_EVAL_CODE_PATH="/home/users0/jagfelga/slu-work/NLG/NLGevaluation/data/"

source /mount/projekte/slu/Projects/glori/bin/tensorflow_1.0/bin/activate

FOLDER=/mount/arbeitsdaten34/projekte/slu/glori//NLG/E2E/human_as_prediction/
for x in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42; do
	PRED=$FOLDER/"$x"_as_predictions.txt
	REFS=$FOLDER/"$x"_references.txt
	bash $NLG_EVAL_CODE_PATH/../run-scripts/evaluate.sh $PRED character $REFS

done

exit
FOLDER=/mount/arbeitsdaten34/projekte/slu/glori//NLG/WebNLG/human_as_prediction/
for x in 0 1 2 3 4 5 6 7; do
	PRED=$FOLDER/"$x"_as_predictions.txt
	REFS=$FOLDER/"$x"_references.txt
	bash $NLG_EVAL_CODE_PATH/../run-scripts/evaluate.sh $PRED character $REFS
done