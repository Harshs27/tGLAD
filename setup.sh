# Create conda environment.
conda create -n tGLAD python=3.8 -y;
conda activate tGLAD;
conda install -c conda-forge notebook -y;
python -m ipykernel install --user --name tGLAD;

# install pytorch (1.9.0 version)
conda install numpy -y;
# conda install pytorch==1.4.0 torchvision==0.5.0 cudatoolkit=10.1 -c pytorch -y;
conda install pytorch torchvision cudatoolkit=10.2 -c pytorch -y;

# Install packages from conda-forge.
conda install -c conda-forge matplotlib -y;
conda install -c plotly plotly -y;
# Install packages from anaconda.
conda install -c anaconda pandas networkx scipy -y;

# Install pip packages
pip install -U scikit-learn
pip install ipywidgets
pip install pyvis
pip install tqdm
# Create environment.yml.
conda env export > environment.yml;