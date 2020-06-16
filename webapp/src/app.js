import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken, removeUserSession, setUserSession } from './utils/common';
import { Header, Grid } from 'semantic-ui-react'

import { BrowserRouter, Switch, NavLink } from 'react-router-dom';

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

  nomatch(event){
    return (
      <div
        className={isMobile ? "bodymain mobile" : "bodymain"}
      >
        <Grid columns={1} doubling stackable>
          <Grid.Column key="0" textAlign="left">
            <Header size='small'>
              Oops! Looks like you're lost.<br/><br/>
              Please visit us at <a href='/login'>/login</a>
            </Header>
          </Grid.Column>
        </Grid>
      </div>
    );
  }

  componentDidMount() {
    document.title = 'Inven3s';

    if (!this.state.token) {
      return;
    }

    axios.get(this.state.apihost + '/user/validate/' + this.state.token)
    .then(response => {
      if(response.status === 200){
        setUserSession(response.headers['access-token'],response.headers['name']);
        this.setState({ authloading: false });
      }
      else{
        removeUserSession();
        this.setState({ authloading: false });
        this.props.history.push('/login');
      }
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
            <NavLink to="/2buy">2Buy</NavLink>
            <NavLink to="/product">Product</NavLink>
          </div>
          <div>
            <Switch>
              <PrivateRoute path="/home" component={Home} />
              <PrivateRoute path="/pan3" component={Pan3} />
              <PrivateRoute path="/2buy" component={ToBuy} />
              <PrivateRoute path="/product" component={Product} />
              <PublicRoute path="/login" component={Login} />
              <PublicRoute component={this.nomatch.bind(this)} />
            </Switch>
          </div>
        </BrowserRouter>
      </div>
    )
  }
}
export default App;

