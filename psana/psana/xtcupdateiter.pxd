cimport numpy as cnp
cnp.import_array() # needed

cdef extern from 'xtcdata/xtc/Dgram.hh' namespace "XtcData":
    cdef cppclass Dgram:
        Dgram() except +
        Xtc xtc

cdef extern from 'xtcdata/xtc/Xtc.hh' namespace "XtcData":
    cdef cppclass Xtc:
        Xtc() except + 
        int sizeofPayload() const

cdef extern from "xtcdata/xtc/NamesId.hh" namespace "XtcData":
    cdef cppclass NamesId:
        NamesId() except +

cdef extern from "xtcdata/xtc/ShapesData.hh" namespace "XtcData":
    cdef cppclass ShapesData:
        ShapesData(NamesId& namesId) except +

cdef extern from "xtcdata/xtc/NameIndex.hh" namespace "XtcData":
    cdef cppclass NameIndex:
        NameIndex() except +

cdef extern from "xtcdata/xtc/DescData.hh" namespace "XtcData":
    cdef cppclass DescData:
        DescData(ShapesData& shapesdata, NameIndex& nameindex) except +

    cdef cppclass AlgVersion:
        AlgVersion(cnp.uint8_t major, cnp.uint8_t minor, cnp.uint8_t micro) except+
        unsigned major()

    cdef cppclass Alg:
        Alg(const char* alg, cnp.uint8_t major, cnp.uint8_t minor, cnp.uint8_t micro)
        const char* name()

    cdef cppclass NameInfo:
        NameInfo(const char* detname, Alg& alg0, const char* dettype, 
                const char* detid, cnp.uint32_t segment0, cnp.uint32_t numarr):
            alg(alg0), segment(segment0)

    cdef cppclass Name:
        enum DataType: UINT8, UINT16, UINT32, UINT64, INT8, INT16, INT32, INT64, FLOAT, DOUBLE
        enum MaxRank: maxrank=5
        Name(const char* name, Alg& alg)
        Name(const char* name, DataType type, int rank, Alg& alg)
        const char* name()
        DataType    type()
        cnp.uint32_t    rank()

    cdef cppclass Shape:
        Shape(unsigned shape[5])
        cnp.uint32_t* shape()

cdef extern from 'xtcdata/xtc/XtcFileIterator.hh' namespace "XtcData":
    cdef cppclass XtcFileIterator:
        XtcFileIterator(int fd, size_t maxDgramSize) except +
        Dgram* next()

cdef extern from 'xtcdata/xtc/XtcUpdateIter.hh' namespace "XtcData":

    cdef cppclass XtcUpdateIter:
        XtcUpdateIter(unsigned numWords) except +
        int process(Xtc* xtc)
        void get_value(int i, Name& name, DescData& descdata)
        void iterate(Xtc* xtc)
        char* get_buf()
        unsigned get_bufsize()
        void copy2buf(char* in_buf, unsigned in_size)
        void addNames(Xtc& xtc, char* detName, unsigned nodeId, unsigned namesId, unsigned segment)
        void addData(Xtc& xtc, unsigned nodeId, unsigned namesId)

