import zipfile, ast, struct, array
def load_npz(path):
    z = zipfile.ZipFile(path); out = {}
    for n in z.namelist():
        b = z.read(n)
        assert b[:6] == b'\x93NUMPY'
        major = b[6]
        if major == 1: hl = struct.unpack('<H', b[8:10])[0]; off = 10
        else: hl = struct.unpack('<I', b[8:12])[0]; off = 12
        h = ast.literal_eval(b[off:off+hl].decode('latin1'))
        data = b[off+hl:]
        d = h['descr']; shape = h['shape']
        code = {'<i8':'q','<f8':'d','<i4':'i','<f4':'f','<f2':None,'|b1':'b','<u8':'Q'}[d] if d in ('<i8','<f8','<i4','<f4','|b1','<u8') else None
        if code is None: out[n[:-4]] = (d, shape); continue
        a = array.array(code); a.frombytes(data)
        a = list(a)
        if len(shape) == 2:
            r, c = shape
            if h.get('fortran_order'): a = [[a[j*r+i] for j in range(c)] for i in range(r)]
            else: a = [a[i*c:(i+1)*c] for i in range(r)]
        out[n[:-4]] = a
    return out
