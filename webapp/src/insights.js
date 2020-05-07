import React from 'react';
import { getUser } from './utils/common';

function Insights(props) {
  const user = getUser();

  return (
    <div>
      Insights for {user}!<br /><br />
      
      Bla bla
    </div>
  )
}
 
export default Insights;
