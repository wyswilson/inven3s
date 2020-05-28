import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken, removeUserSession, setUserSession } from './utils/common';

import { BrowserRouter, Switch, NavLink, Redirect } from 'react-router-dom';

import Login from './login';
import Inventory from './inventory';
import Home from './home';
import Product from './product';

import PrivateRoute from './utils/private-route';
import PublicRoute from './utils/public-route';

class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      apihost: 'https://13.229.135.211',
      token: getToken(),
      authloading: true
    };
  }

  componentDidMount() {
    document.title = 'Inven3s';

    if (!this.state.token) {
      return;
    }

    axios.get(this.state.apihost + '/user/validate/' + this.state.token)
    .then(response => {
      setUserSession(response.headers['access-token'],response.headers['name']);
      this.setState({ authloading: false });
    }).catch(error => {
      removeUserSession();
      this.setState({ authloading: false });
      this.props.history.push('/login');
    });
  }


  render() {
    return (
      <div className="container">
        <BrowserRouter>
          <div className={isMobile ? "navheader mobile" : "navheader"}>
            <NavLink to="/home">Home</NavLink>
            <NavLink to="/inventory">Inventory</NavLink>
            <NavLink to="/product">Product</NavLink>
          </div>
          <div>
            <Switch>
              <PrivateRoute path="/home" component={Home} />
              <PrivateRoute path="/inventory" component={Inventory} />
              <PrivateRoute path="/product" component={Product} />
              <PublicRoute path="/login" component={Login} />
              <PublicRoute exact path="/">
                <Redirect to="/login" />
              </PublicRoute>
            </Switch>
          </div>
        </BrowserRouter>
      </div>
    )
  }
}
export default App;

