eval "$(conda shell.bash hook)"

conda activate backend
echo "Activated conda env"
python3 backend.py
