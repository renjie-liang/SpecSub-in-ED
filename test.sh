
#gnome-terminal --tab  --title 'server' -- bash -c "python3 ./lib/twocloud_server.py; exec bash"

python3 run.py \
	--name test_rj \
	--noise_db -10 \
	--input_dir './data/test/' \
	--inc 2 \
	--wlen 4 \
	--NIS 2 \
	--debug
