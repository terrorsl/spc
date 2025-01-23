import argparse

from spc import SimplePDFCreate

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, required=True, help="load project")
    parser.add_argument('--noprogress', default=False, help="disable progress message")
    args = parser.parse_args()

    spc = SimplePDFCreate()
    doc = spc.load(args.filename)
    print(f'save document')
    doc.save()
    print(f'done')
