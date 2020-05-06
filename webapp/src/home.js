import React from 'react';
import { getUser, removeUserSession } from './utils/common';

function Home(props) {
  const user = getUser();

  // handle click event of logout button
  const handleLogout = () => {
    removeUserSession();
    props.history.push('/login');
  }

  return (
    <div>
      Home for {user}!<br /><br />
      
      <input type="button" onClick={handleLogout} value="Logout" />
    </div>
  );
}
 
export default Home;
