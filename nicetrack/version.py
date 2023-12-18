'''
Created on 2023-06-19

@author: wf
'''
import nicetrack
class Version(object):
    """
    Version handling for nicetrack
    """
    name = "nicetrack"
    version = nicetrack.__version__
    date = '2023-08-16'
    updated = '2023-11-18'
    description = 'Nice 3D Track handling'
    
    authors = 'Wolfgang Fahl'
    
    doc_url="https://wiki.bitplan.com/index.php/nicetrack"
    chat_url="https://github.com/WolfgangFahl/nicetrack/discussions"
    cm_url="https://github.com/WolfgangFahl/nicetrack"

    license = f'''Copyright 2023 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.'''
    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""