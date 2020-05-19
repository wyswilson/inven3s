import React from 'react';
import { BrowserRouter, Switch, NavLink, Redirect } from 'react-router-dom';
import axios from 'axios';
import { Container } from 'semantic-ui-react'

import Login from './login';
import Inventory from './inventory';
import Home from './home';
import Product from './product';

import PrivateRoute from './utils/private-route';
import PublicRoute from './utils/public-route';
import { getToken, removeUserSession, setUserSession } from './utils/common';

class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      apihost: 'http://127.0.0.1:8989',
      token: getToken(),
      authloading: true
    };
  }

  componentDidMount() {
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
    });
  }


  render() {
    return (
      <Container textAlign="left" className="App" fluid>
        <BrowserRouter>
          <div>
            <div className="header nav">
              <NavLink activeClassName="active" to="/home">Home</NavLink>
              <NavLink activeClassName="active" to="/inventory">Inventory</NavLink>
              <NavLink activeClassName="active" to="/product">Product</NavLink>
            </div>
            <div className="content">
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
      </Container>

    )
  }
}
export default App;

