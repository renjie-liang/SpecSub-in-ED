gnome-terminal --tab  --title 'server' -- bash -c "python3 ./lib/twocloud_server.py; exec bash"

python3 run.py \
	--name short_rj \
	--noise_db -0 \
	--input_dir './data/short/' \
	--inc 160 \
	--wlen 400 \
	--NIS 23 \

