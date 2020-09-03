import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken, removeUserSession, setUserSession } from './utils/common';
import { Header, Grid } from 'semantic-ui-react'

import { BrowserRouter, Switch, NavLink, Redirect } from 'react-router-dom';

import Login from './login';
import Pantry from './pantry';
import Home from './home';
import Products from './products';
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
    const permissiblehosts = ['inven3s.com','127.0.0.1','localhost']
    const hostname = window.location.hostname;
    console.log(hostname);

    if(!permissiblehosts.includes(hostname)){
      window.location.href = 'https://google.com'; 
      return null;
    }
    else{
      if (!this.state.token) {
        return null;
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
  }


  render() {
    return (
      <div className="container">
        <BrowserRouter>
          <div className={isMobile ? "navheader mobile" : "navheader"}>
            <NavLink to="/home">Home</NavLink>
            <NavLink to="/pantry">Pantry</NavLink>
            <NavLink to="/tobuy">ToBuy</NavLink>
            <NavLink to="/products">Products</NavLink>
          </div>
          <div>
            <Switch>
              <PrivateRoute path="/home" component={Home} />
              <PrivateRoute path="/pantry" component={Pantry} />
              <PrivateRoute path="/tobuy" component={ToBuy} />
              <PrivateRoute path="/products" component={Products} />
              <PublicRoute path="/login" component={Login} />
              <PublicRoute path="/inventory" component={Login} />
              <PublicRoute exact path="/">
                <Redirect to="/login" />
              </PublicRoute>
              <PublicRoute component={this.nomatch.bind(this)} />
            </Switch>
          </div>
        </BrowserRouter>
      </div>
    )
  }
}
export default App;

