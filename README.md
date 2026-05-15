# Geomodel Compression Solution

## Approach
Our solution uses a **hierarchical parsing** strategy to identify all model dependencies and applies **numerical quantization** to `.inc` and `.DATA` files to achieve high compression while maintaining **1e-5** relative error precision. 

### Key Features:
- **Deck Hierarchy Parser**: Recursively finds all `INCLUDE` files.
- **Float Quantization**: Reduces numerical precision to 6 significant digits.
- **Standard Library Only**: High portability, no external dependencies required.

## Installation
No installation required. Uses standard Python 3.10 libraries.

## Usage
### Compress
```bash
python compress.py --input path/to/model --output model.tar.gz
```

### Decompress
```bash
python decompress.py --input model.tar.gz --output path/to/restored_model
```
