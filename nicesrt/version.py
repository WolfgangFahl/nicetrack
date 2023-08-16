'''
Created on 2023-06-19

@author: wf
'''
import nicesrt
class Version(object):
    """
    Version handling for nicesrt
    """
    name = "nicesrt"
    version = nicesrt.__version__
    date = '2023-08-16'
    updated = '2023-08-16'
    description = 'Nice Subtitle Telemetry handling',
    
    authors = 'Wolfgang Fahl'
    
    doc_url="https://wiki.bitplan.com/index.php/nicesrt"
    chat_url="https://github.com/WolfgangFahl/nicesrt/discussions"
    cm_url="https://github.com/WolfgangFahl/nicesrt"

    license = f'''Copyright 2023 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.'''
    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""