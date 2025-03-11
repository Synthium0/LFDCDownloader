
# LFDCDownloader
A script that makes downloading packages from digitalcontent easier


## Getting Started
Ensure you have all the modules required for this project by running
```
pip install -r requirements.txt
```
## Usage
`python main.py <TARGET_ID>`

Or, if you'd like to decompress the package immediately after it downloads (if it's an .lf3 package)

`python main.py <TARGET_ID> -d`

If you'd like to have the program generate a .tar file which can be installed onto your LeapFrog device via [LFManager](https://github.com/lfhacks/LFManager/releases), then:

`python main.py <TARGET_ID> -i`

---

> This project is neither endorsed by nor affiliated with LFHacks in any capacity.
