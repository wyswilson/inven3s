import React, { useState, useEffect } from 'react';
import { BrowserRouter, Switch, NavLink } from 'react-router-dom';
import axios from 'axios';

import Login from './login';
import Inventory from './inventory';
import Insights from './insights';

import PrivateRoute from './utils/private-route';
import PublicRoute from './utils/public-route';
import { getToken, removeUserSession, setUserSession } from './utils/common';

function App(props) {
  const [authLoading, setAuthLoading] = useState(true);
  let authaction;

  const handleLogout = () => {
    removeUserSession();
  }

  useEffect(() => {
    const token = getToken();
    
    if (!token) {
      return;
    }

    axios.get(`http://127.0.0.1:8989/user/validate/${token}`)
    .then(response => {
      setUserSession(response.headers['access-token'],response.headers['name']);
      setAuthLoading(false);
    }).catch(error => {
      removeUserSession();
      setAuthLoading(false);
    });
  }, []);

  if (authLoading && getToken()) {
    return <div className="error">checking authentication...</div>
  }

  if (!authLoading){
    authaction = <NavLink to="/login" onClick={handleLogout}>logout</NavLink>;
  }


  return (
    <div className="App">
      <BrowserRouter>
        <div>
          <div className="header">
            <NavLink exact activeClassName="active" to="/insights">insights</NavLink>
            <NavLink activeClassName="active" to="/inventory">inventory</NavLink><small></small>
            {authaction}
          </div>
          <div className="content">
            <Switch>
              <PrivateRoute exact path="/insights" component={Insights} />
              <PrivateRoute path="/inventory" component={Inventory} />
              <PublicRoute path="/login" component={Login} />
            </Switch>
          </div>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;
