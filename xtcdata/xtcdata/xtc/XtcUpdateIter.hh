#ifndef XTCDATA_DEBUGITER_H
#define XTCDATA_DEBUGITER_H

/*
 * class XtcUpdateIter provides access to all types of xtc
 */

#include "xtcdata/xtc/XtcIterator.hh"
#include "xtcdata/xtc/DescData.hh"
#include "xtcdata/xtc/ShapesData.hh"

#define BUFSIZE 0x1000000

namespace XtcData
{

class XtcUpdateIter : public XtcData::XtcIterator
{
public:
    enum {Stop, Continue};
    
    XtcUpdateIter(unsigned numWords) : XtcData::XtcIterator(), _numWords(numWords) {
        _bufsize = 0;
        _buf = (char *) malloc(BUFSIZE);
    }

    ~XtcUpdateIter() {
        free(_buf);
    }
    
    virtual int process(XtcData::Xtc* xtc);
    
    void get_value(int i, Name& name, DescData& descdata);

    char* get_buf(){
        return _buf;
    }

    unsigned get_bufsize(){
        return _bufsize;
    }

    void copy2buf(char* in_buf, unsigned in_size);
    void addNames(Xtc& xtc, char* detName, unsigned nodeId, unsigned namesId, unsigned segment);
    void addData(Xtc& xtc, unsigned nodeId, unsigned namesId);


private:
    NamesLookup _namesLookup;
    unsigned _numWords;
    char* _buf;
    unsigned _bufsize;
}; // end class XtcUpdateIter

}; // end namespace XtcData

#endif //