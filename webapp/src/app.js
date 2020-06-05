import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken, removeUserSession, setUserSession } from './utils/common';

import { BrowserRouter, Switch, NavLink, Redirect } from 'react-router-dom';

import Login from './login';
import Pan3 from './pan3';
import Home from './home';
import Product from './product';
import ToBuy from './tobuy';

import PrivateRoute from './utils/private-route';
import PublicRoute from './utils/public-route';


class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      //apihost: 'http://127.0.0.1:88',
      apihost: 'https://inven3s.xyz',
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
            <NavLink to="/pan3">Pan3</NavLink>
            <NavLink to="/product">Product</NavLink>
            <NavLink to="/2buy">2Buy</NavLink>
          </div>
          <div>
            <Switch>
              <PrivateRoute path="/home" component={Home} />
              <PrivateRoute path="/pan3" component={Pan3} />
              <PrivateRoute path="/product" component={Product} />
              <PrivateRoute path="/2buy" component={ToBuy} />
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

