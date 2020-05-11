import React, { useState, useEffect } from 'react';
import { BrowserRouter, Switch, NavLink, Redirect } from 'react-router-dom';
import axios from 'axios';

import Login from './login';
import Inventory from './inventory';
import Home from './home';

import PrivateRoute from './utils/private-route';
import PublicRoute from './utils/public-route';
import { getToken, removeUserSession, setUserSession } from './utils/common';

function App(props) {
  const [authLoading, setAuthLoading] = useState(true);

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
    return <div className="error">authenticating</div>
  }

  return (
    <div className="App">
      <BrowserRouter>
        <div>
          <div className="header nav">
            <NavLink activeClassName="active" to="/home">home</NavLink>
            <NavLink activeClassName="active" to="/inventory">inventory</NavLink>
          </div>
          <div className="content">
            <Switch>
              <PrivateRoute path="/home" component={Home} />
              <PrivateRoute path="/inventory" component={Inventory} />
              <PublicRoute path="/login" component={Login} />
              <PublicRoute exact path="/">
                <Redirect to="/login" />
              </PublicRoute>
            </Switch>
          </div>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;
