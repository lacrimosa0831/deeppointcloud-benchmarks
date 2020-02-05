
from typing import Optional, List, Callable
import math
import hashlib

import torch
from torch_geometric.data import InMemoryDataset, Data, Dataset
from overrides import overrides
import numpy as np

from src.data.base_dataset import BaseDataset
from src.data.base_patchable_pointcloud import BasePatchablePointCloud


class PatchDataset(torch.utils.data.Dataset):
    '''Class representing datasets over multiple patchable pointclouds. 

    This class basically forwards methods to the underlying list of patch datasets

    A dataset will usually consist of multiple pointclouds, each of which must be sampled
    as patches. Each pointcloud is represented by a BasePatchablePointCloud. This class provides 
    an interface to a list of BasePatchablePointClouds
    '''

    def __init__(self, patchable_clouds: List[BasePatchablePointCloud]):
        self._patchable_clouds = patchable_clouds

    @property
    def patchable_clouds(self) -> List[BasePatchablePointCloud]:
        return self._patchable_clouds

    def __len__(self):
        return sum(len(pd) for pd in self.patchable_clouds)

    def __getitem__(self, idx):
        
        i = 0

        for pds in self.patchable_clouds:
            if idx < i + len(pds):
                return pds[idx - i]
            i += len(pds)

    #forward all attribute calls to the underlying datasets
    #(e.g. num_features)
    def __getattr__(self, name):
        return getattr(self.patchable_clouds[0], name)

class LargePatchDatase(torch.utils.data.IterableDataset):
    '''like BaseMultiCloudPatchDatasets, but for datasets that are too large to fit in memory''' 

    def __init__(self, 
        backing_dataset: torch.utils.data.Dataset, 
        make_patchable_cloud: Callable[[Data], BasePatchablePointCloud],
        samples_per_dataset = 10,
        num_loaded_datasets = 4
    ):
        self._backing_dataset = backing_dataset
        self._make_patchable_cloud = make_patchable_cloud
        self._samples_per_dataset = samples_per_dataset
        self._num_loaded_datasets = num_loaded_datasets

        self._num_samples_taken = 0
        self._patch_dataset = None
        self.cycle()

    @overrides
    def __iter__(self):
        return self

    def __next__(self):
        if self._num_samples_taken > self._samples_per_dataset * self._num_loaded_datasets:
            self.cycle()

        idx = np.random.choice(len(self._mc_patch_dataset))
        return self._mc_patch_dataset[idx]

    #forward all attribute calls to the underlying datasets
    #(e.g. num_features)
    def __getattr__(self, name):
        return getattr(self.patchable_clouds[0], name)

    def cycle(self):
        patchableCloudIndexes = np.random.choice(
                len(self._backing_dataset),
                size=self._num_loaded_datasets,
                replace=False,
        )

        self._patch_dataset = PatchDataset([
            self._make_patchable_cloud(self._dataset[idx]) 
            for idx in patchableCloudIndexes
        ])
        self._num_samples_taken = 0







        



    



    

        
    

    


