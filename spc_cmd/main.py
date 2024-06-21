import argparse

from spc import SimplePDFCreate

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, required=True, help="load")
    args = parser.parse_args()

    spc = SimplePDFCreate()
    doc = spc.load(args.filename)
    doc.save()
