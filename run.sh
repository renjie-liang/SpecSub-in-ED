#gnome-terminal --tab  --title 'server' -- bash -c "python3 ./lib/twocloud_server.py; exec bash"

python3 run.py \
	--name spch1_snr-15 \
	--noise_db -15 \
	--input_dir './data/' \
	--inc 160 \
	--wlen 400 \
	--NIS 5 \

