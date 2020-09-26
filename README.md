# depression_identification
A Graph Convolutional Network Approach for Depression Detection using EEG based Brain Networks

Present literature in using EEG for Depression Detection has focused on exploiting either the temporal or spatial structure from EEG Data. Graph Convolutional Networks allow incorporating both in an efficient manner and can outperform classical classification tech- niques.
Method and Results: EEG Data is first augmented by creating 10 second segments. For each sample, the graph structure is created by computing the correlation matrix across EEG channels. Higuchi’s Fractal Dimension and Sample Entropy at each channel are used as node signals. A Deep GCN with 6 GCN layers and 3 Dense layers is trained using PRE- DICT EEG dataset with an achieved accuracy of 82.8 ± 1.6%. This captures the single channel features of the EEG signals along with retaining their spatial structure, in the most efficient way, avoiding computation on extracting multi channel features(inter-channel de- pendence) explicitly. 

![Alt text](relative/path/to/img.jpg?raw=true "Title")
