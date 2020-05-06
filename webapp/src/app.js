import React, { useState, useEffect } from 'react';
import { BrowserRouter, Switch, Route, NavLink } from 'react-router-dom';
import axios from 'axios';

import Login from './login';
import Inventory from './inventory';
import Home from './home';

import PrivateRoute from './utils/private-route';
import PublicRoute from './utils/public-route';
import { getToken, removeUserSession, setUserSession } from './utils/common';

function App() {
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      return;
    }

    axios.get(`http://127.0.0.1:8989/user/validate/${token}`)
    .then(response => {
      setUserSession(response.headers['access-token'],response.headers['identifier']);
      setAuthLoading(false);
    }).catch(error => {
      removeUserSession();
      setAuthLoading(false);
    });
  }, []);

  if (authLoading && getToken()) {
    return <div className="content">checking authentication...</div>
  }

  return (
    <div className="App">
      <BrowserRouter>
        <div>
          <div className="header">
            <NavLink exact activeClassName="active" to="/">home</NavLink>
            <NavLink activeClassName="active" to="/inventory">inventory</NavLink><small></small>
          </div>
          <div className="content">
            <Switch>
              <Route exact path="/" component={Home} />
              <PublicRoute path="/login" component={Login} />
              <PrivateRoute path="/inventory" component={Inventory} />
            </Switch>
          </div>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;
