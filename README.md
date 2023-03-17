## Are uGLAD? Time will tell!  
### Introducing the `tGLAD` framework for multivariate time series segmentation  

we introduce a novel approach for multivariate time series segmentation using conditional independence (CI) graphs. CI graphs are probabilistic graphical models that represents the partial correlations between the nodes. We propose a domain agnostic multivariate segmentation framework `tGLAD` which draws a parallel between the CI graph nodes and the variables of the time series. If we apply the graph recovery model `uGLAD` to a short interval of the time series, it will result in a CI graph that shows partial correlations among the variables. We extend this to the time series by utilizing a sliding window to create a batch of intervals and then run a single `uGLAD` model in multitask learning mode to recover all the CI graphs simultaneously. As a result, we obtain a corresponding temporal CI graphs representation of the multivariate time series. We then designed a trajectory tracking algorithm to study the evolution of these graphs across distinct intervals to determine a suitable segmentation. `tGLAD` provides a competitive time complexity of $O(N)$ for settings where number of variables D<<N. 
 



## Setup  
The `setup.sh` file contains the complete procedure of creating a conda environment to run `tGLAD` model. run `bash setup.sh`    
In case of dependencies conflict, one can alternatively use this command `conda env create --name tGLAD --file=environment.yml`.  

## demo     
A minimalist working example of `tGLAD` is given in `demo_tglad.ipynb`.

## Citation
If you find this method useful, kindly cite the following paper:
- `Are uGLAD? Time will tell!`: [arxiv](<link>)  

@article{}


