#pragma once

#include "drp.hh"
#include "Detector.hh"
#include "EventBatcher.hh"
#include "xtcdata/xtc/Xtc.hh"
#include "xtcdata/xtc/NamesId.hh"
#include <Python.h>

namespace Drp {

class Opal : public Detector
{
public:
    Opal(Parameters* para, MemPool* pool);
    nlohmann::json connectionInfo() override;
    void connect(const nlohmann::json&, const std::string& collectionId) override;
    unsigned configure(const std::string& config_alias, XtcData::Xtc& xtc) override;
    void event(XtcData::Dgram& dgram, PGPEvent* event) override;
    Pds::TimingHeader* getTimingHeader(uint32_t index) const override
    {
        EvtBatcherHeader& ebh = *static_cast<EvtBatcherHeader*>(m_pool->dmaBuffers[index]);
        // skip past the event-batcher header
        return static_cast<Pds::TimingHeader*>(ebh.next());
    }
private:
    void _addJson(XtcData::Xtc& xtc, XtcData::NamesId& configNamesId, const std::string& config_alias);
    unsigned _getPaddr();
private:
    enum {ConfigNamesIndex = NamesIndex::BASE, EventNamesIndex};
    unsigned          m_readoutGroup;
    XtcData::NamesId  m_evtNamesId;
    std::string       m_connect_json;
    PyObject*         m_root;
    unsigned          m_paddr;
    unsigned          m_rows;
    unsigned          m_columns;
  };

}