# Copyright (c) 2020, Soohwan Kim. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import torch.nn as nn

from torch import Tensor
from typing import Tuple
from kospeech.models.jasper.decoder import JasperDecoder
from kospeech.models.jasper.encoder import JasperEncoder
from kospeech.models.jasper import (
    Jasper10x5EncoderConfig,
    Jasper10x5DecoderConfig,
)


class Jasper(nn.Module):
    """
    Jasper: An End-to-End Convolutional Neural Acoustic Model
    Jasper (Just Another Speech Recognizer), an ASR model comprised of 54 layers proposed by NVIDIA.
    Jasper achieved sub 3 percent word error rate (WER) on the LibriSpeech dataset.
    More details: https://arxiv.org/pdf/1904.03288.pdf

    Args:
        num_classes (int): number of classification
        version (str): version of jasper. Marked as BxR: B - number of blocks, R - number of sub-blocks

    Inputs: inputs, input_lengths, residual
        - **inputs**: tensor contains input sequence vector
        - **input_lengths**: tensor contains sequence lengths
        - **residual**: tensor contains residual vector

    Returns: output, output_lengths
        - **output**: tensor contains output sequence vector
        - **output**: tensor contains output sequence lengths
    """

    def __init__(self, num_classes: int, version: str = '10x5') -> None:
        super(Jasper, self).__init__()
        supported_versions = {
            '10x5': {
                'enooder_config': Jasper10x5EncoderConfig(num_blocks=10, num_sub_blocks=5),
                'decoder_config': Jasper10x5DecoderConfig(num_classes),
            }
        }
        assert version.lower() in supported_versions.keys(), "Unsupported Version: {}".format(version)

        self.encoder = JasperEncoder(config=supported_versions[version]['encoder_config'])
        self.decoder = JasperDecoder(config=supported_versions[version]['decoder_config'])

    def forward(self, inputs: Tensor, input_lengths: Tensor) -> Tuple[Tensor, Tensor]:
        """
        inputs: BxTxD
        input_lengths: B
        """
        encoder_outputs, output_lengths = self.encoder(inputs, input_lengths)
        output, output_lengths = self.decoder(encoder_outputs, output_lengths)
        return output, output_lengths