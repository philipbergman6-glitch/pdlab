# Cross-check: pdlab vs axelrod 4.14.0 (deterministic strategies, 200 rounds)

| pdlab A | pdlab B | pdlab (A,B) | axelrod (A,B) | match |
|---|---|---|---|---|
| ALLC | ALLC | (600, 600) | (600, 600) | yes |
| ALLC | ALLD | (0, 1000) | (0, 1000) | yes |
| ALLC | TFT | (600, 600) | (600, 600) | yes |
| ALLC | STFT | (597, 602) | (597, 602) | yes |
| ALLC | TF2T | (600, 600) | (600, 600) | yes |
| ALLC | GRIM | (600, 600) | (600, 600) | yes |
| ALLC | WSLS | (600, 600) | (600, 600) | yes |
| ALLC | CTFT | (600, 600) | (600, 600) | yes |
| ALLC | ALT | (300, 800) | (300, 800) | yes |
| ALLC | SOFTMAJ | (600, 600) | (600, 600) | yes |
| ALLC | HARDMAJ | (597, 602) | (597, 602) | yes |
| ALLC | PROBER | (6, 996) | (6, 996) | yes |
| ALLC | GRADUAL | (600, 600) | (600, 600) | yes |
| ALLD | ALLD | (200, 200) | (200, 200) | yes |
| ALLD | TFT | (204, 199) | (204, 199) | yes |
| ALLD | STFT | (200, 200) | (200, 200) | yes |
| ALLD | TF2T | (208, 198) | (208, 198) | yes |
| ALLD | GRIM | (204, 199) | (204, 199) | yes |
| ALLD | WSLS | (600, 100) | (600, 100) | yes |
| ALLD | CTFT | (204, 199) | (204, 199) | yes |
| ALLD | ALT | (600, 100) | (600, 100) | yes |
| ALLD | SOFTMAJ | (204, 199) | (204, 199) | yes |
| ALLD | HARDMAJ | (200, 200) | (200, 200) | yes |
| ALLD | PROBER | (208, 198) | (208, 198) | yes |
| ALLD | GRADUAL | (340, 165) | (340, 165) | yes |
| TFT | TFT | (600, 600) | (600, 600) | yes |
| TFT | STFT | (500, 500) | (500, 500) | yes |
| TFT | TF2T | (600, 600) | (600, 600) | yes |
| TFT | GRIM | (600, 600) | (600, 600) | yes |
| TFT | WSLS | (600, 600) | (600, 600) | yes |
| TFT | CTFT | (600, 600) | (600, 600) | yes |
| TFT | ALT | (498, 503) | (498, 503) | yes |
| TFT | SOFTMAJ | (600, 600) | (600, 600) | yes |
| TFT | HARDMAJ | (500, 500) | (500, 500) | yes |
| TFT | PROBER | (599, 599) | (599, 599) | yes |
| TFT | GRADUAL | (600, 600) | (600, 600) | yes |
| STFT | STFT | (200, 200) | (200, 200) | yes |
| STFT | TF2T | (602, 597) | (602, 597) | yes |
| STFT | GRIM | (203, 203) | (203, 203) | yes |
| STFT | WSLS | (401, 401) | (401, 401) | yes |
| STFT | CTFT | (500, 500) | (500, 500) | yes |
| STFT | ALT | (500, 500) | (500, 500) | yes |
| STFT | SOFTMAJ | (500, 500) | (500, 500) | yes |
| STFT | HARDMAJ | (200, 200) | (200, 200) | yes |
| STFT | PROBER | (600, 595) | (600, 595) | yes |
| STFT | GRADUAL | (601, 596) | (601, 596) | yes |
| TF2T | TF2T | (600, 600) | (600, 600) | yes |
| TF2T | GRIM | (600, 600) | (600, 600) | yes |
| TF2T | WSLS | (600, 600) | (600, 600) | yes |
| TF2T | CTFT | (600, 600) | (600, 600) | yes |
| TF2T | ALT | (300, 800) | (300, 800) | yes |
| TF2T | SOFTMAJ | (600, 600) | (600, 600) | yes |
| TF2T | HARDMAJ | (597, 602) | (597, 602) | yes |
| TF2T | PROBER | (201, 216) | (201, 216) | yes |
| TF2T | GRADUAL | (600, 600) | (600, 600) | yes |
| GRIM | GRIM | (600, 600) | (600, 600) | yes |
| GRIM | WSLS | (600, 600) | (600, 600) | yes |
| GRIM | CTFT | (600, 600) | (600, 600) | yes |
| GRIM | ALT | (597, 107) | (597, 107) | yes |
| GRIM | SOFTMAJ | (600, 600) | (600, 600) | yes |
| GRIM | HARDMAJ | (203, 203) | (203, 203) | yes |
| GRIM | PROBER | (207, 202) | (207, 202) | yes |
| GRIM | GRADUAL | (600, 600) | (600, 600) | yes |
| WSLS | WSLS | (600, 600) | (600, 600) | yes |
| WSLS | CTFT | (600, 600) | (600, 600) | yes |
| WSLS | ALT | (450, 450) | (450, 450) | yes |
| WSLS | SOFTMAJ | (600, 600) | (600, 600) | yes |
| WSLS | HARDMAJ | (104, 599) | (104, 599) | yes |
| WSLS | PROBER | (401, 401) | (401, 401) | yes |
| WSLS | GRADUAL | (600, 600) | (600, 600) | yes |
| CTFT | CTFT | (600, 600) | (600, 600) | yes |
| CTFT | ALT | (498, 503) | (498, 503) | yes |
| CTFT | SOFTMAJ | (600, 600) | (600, 600) | yes |
| CTFT | HARDMAJ | (500, 500) | (500, 500) | yes |
| CTFT | PROBER | (599, 599) | (599, 599) | yes |
| CTFT | GRADUAL | (600, 600) | (600, 600) | yes |
| ALT | ALT | (400, 400) | (400, 400) | yes |
| ALT | SOFTMAJ | (800, 300) | (800, 300) | yes |
| ALT | HARDMAJ | (500, 500) | (500, 500) | yes |
| ALT | PROBER | (503, 498) | (503, 498) | yes |
| ALT | GRADUAL | (262, 537) | (262, 537) | yes |
| SOFTMAJ | SOFTMAJ | (600, 600) | (600, 600) | yes |
| SOFTMAJ | HARDMAJ | (500, 500) | (500, 500) | yes |
| SOFTMAJ | PROBER | (599, 599) | (599, 599) | yes |
| SOFTMAJ | GRADUAL | (600, 600) | (600, 600) | yes |
| HARDMAJ | HARDMAJ | (200, 200) | (200, 200) | yes |
| HARDMAJ | PROBER | (501, 496) | (501, 496) | yes |
| HARDMAJ | GRADUAL | (601, 596) | (601, 596) | yes |
| PROBER | PROBER | (204, 204) | (204, 204) | yes |
| PROBER | GRADUAL | (599, 599) | (599, 599) | yes |
| GRADUAL | GRADUAL | (600, 600) | (600, 600) | yes |

**91/91 deterministic pairings agree exactly.**


# Memory-one vectors

- GTFT: pdlab (1.0, 0.333333, 1.0, 0.333333); axelrod GTFT: {(C, C): 1, (C, D): 0.3333333333333333, (D, C): 1, (D, D): 0.3333333333333333}
- EXTORT2: pdlab (0.888889, 0.5, 0.333333, 0.0); axelrod ZD-Extort-2: {(C, C): np.float64(0.8888888888888888), (C, D): np.float64(0.5), (D, C): np.float64(0.3333333333333333), (D, D): np.float64(0.0)}
- ZDGTFT2: pdlab (1.0, 0.125, 1.0, 0.25); axelrod ZD-GTFT-2: {(C, C): np.float64(1.0), (C, D): np.float64(0.125), (D, C): np.float64(1.0), (D, D): np.float64(0.25)}
