import React from 'react';
import { BrowserRouter, Switch, NavLink, Redirect } from 'react-router-dom';
import axios from 'axios';

import Login from './login';
import Inventory from './inventory';
import Home from './home';
import Product from './product';

import PrivateRoute from './utils/private-route';
import PublicRoute from './utils/public-route';
import { getToken, removeUserSession, setUserSession } from './utils/common';
import {isMobile} from 'react-device-detect';

class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      apihost: 'http://13.229.67.229:8989',
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
      <div className="App">
        <BrowserRouter>
          <div>
            <div className="header nav">
              <NavLink to="/home">Home</NavLink>
              <NavLink to="/inventory">Inventory</NavLink>
              <NavLink to="/product">Product</NavLink>
            </div>
            <div className={isMobile ? "pagebody mobile" : "pagebody"}>
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
          </div>
        </BrowserRouter>
      </div>
    )
  }
}
export default App;

