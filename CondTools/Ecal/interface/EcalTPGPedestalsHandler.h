#ifndef ECAL_TPG_PEDESTALS_HANDLER_H
#define ECAL_TPG_PEDESTALS_HANDLER_H

#include <vector>
#include <typeinfo>
#include <string>
#include <map>
#include <iostream>
#include <time.h>

#include "CondCore/PopCon/interface/PopConSourceHandler.h"
#include "FWCore/ParameterSet/interface/ParameterSetfwd.h"


#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CondCore/DBOutputService/interface/PoolDBOutputService.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/EventSetupRecordKey.h"


#include "CondFormats/EcalObjects/interface/EcalTPGPedestals.h"
#include "CondFormats/DataRecord/interface/EcalTPGPedestalsRcd.h"

#include "OnlineDB/EcalCondDB/interface/all_monitoring_types.h"
#include "OnlineDB/Oracle/interface/Oracle.h"
#include "OnlineDB/EcalCondDB/interface/EcalCondDBInterface.h"

#include "DataFormats/EcalDetId/interface/EEDetId.h"
#include "DataFormats/EcalDetId/interface/EBDetId.h"
#include "DataFormats/Provenance/interface/Timestamp.h"

namespace edm {
  class ParameterSet;
  class Event;
  class EventSetup;
}

namespace popcon
{


	class EcalTPGPedestalsHandler : public popcon::PopConSourceHandler<EcalTPGPedestals>
	{

	  std::string to_string( char value[]) {
	    std::ostringstream streamOut;
	    streamOut << value;
	    return streamOut.str();
	  }

		public:

                        EcalTPGPedestalsHandler(edm::ParameterSet const & );
			~EcalTPGPedestalsHandler(); 
			void getNewObjects();

			std::string id() const { return m_name;}

			void readFromFile(const char* inputFile) ;
			void writeFile(const char* inputFile);


			EcalCondDBInterface* econn;

		private:
			const EcalTPGPedestals * mypedestals;

			unsigned int m_firstRun ;
			unsigned int m_lastRun ;
			
			std::string m_location;
			std::string m_gentag;
			std::string m_sid;
			std::string m_user;
			std::string m_pass;
                        std::string m_locationsource;
                        std::string m_name;
			unsigned int m_runnr;
			std::string m_runtype;
			std::string m_i_tag;
			int m_i_version;
			unsigned int m_i_run_number;
			int m_i_ped;

	};
}
#endif

