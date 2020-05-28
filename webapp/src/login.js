import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { setUserSession } from './utils/common';
import { List, Header, Container, Button, Card, Message, Grid } from 'semantic-ui-react'
import Field from './field.js';

class Login extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      apihost: 'http://13.229.67.229:8989',
      email: '',
      password: '',
      message: '',
      success: false,
      tried: false,
    };
  }
  
  updatecredentials(field,value) {
    if(field === 'email'){
      this.setState({ email:value });
    }
    if(field === 'password'){
      this.setState({ password:value });
    }
  }

  authenticate(event){
    this.setState({ message: 'authenticating' });
    this.setState({ tried: true });

    console.log('authenticate [' + this.state.email + ']');

    axios.post(this.state.apihost + '/user/login', {},
      {
       auth: {
        username: this.state.email,
        password: this.state.password
      }
    })
    .then(response => {
      if(response.status === 200){
        this.setState({ success: true});
        setUserSession(response.headers['access-token'],response.headers['name']);
        this.props.history.push({
          pathname: '/home',
          state: { sessionid: 'xxxxxxxxxx' }
        });
      }
    })
    .catch(error => {
      this.setState({ success: false});
      const errresponse = error.response;
      if(errresponse){
        if(errresponse.status === 401){
          this.setState({ message:'incorrect username and/or password' });
        }
        else{
          this.setState({ message:errresponse });
        }
      }
      else{
        this.setState({ message:'server unreachable' });
      }
    });
  }
  
  updatemessage(){
    if(this.state.tried){
      return (
        <Card raised>
            <Message size='tiny' warning={this.state.tried && !this.state.success}
              header={this.state.message}
            />
        </Card>
      )
    }
    else{
      return (
        <Button color="grey" className="fullwidth">
        Sign up</Button>
      )
    }
  }

  render() {
    return (
      <Container fluid>
        <Container fluid
          className={isMobile ? "pagebody login mobile" : "pagebody login"}
        >
          <Grid columns={2} doubling stackable>
            <Grid.Column textAlign="center" verticalAlign="middle">
              <Header
                content='Helping you reduce waste at home with AI solutions'
                className={isMobile ? "text main mobile" : "text main"}
              />
              <Header
                content='...starting with your pantry'
                className={isMobile ? "text secondary mobile" : "text secondary"}
              />
            </Grid.Column>
            <Grid.Column textAlign="center">
              <Card raised key="1" fluid>
                <Card.Content>
                  <Field label="email" type="text" active={false}
                    parentCallback={this.updatecredentials.bind(this)}/>
                  <Field label="password" type="password" active={false}
                  parentCallback ={this.updatecredentials.bind(this)}/>
                </Card.Content>
                <Card.Content extra>
                  <Grid columns={2}>
                    <Grid.Column>
                      <Button color="grey" className="fullwidth" onClick={this.authenticate.bind(this)}>
                      Login</Button>
                    </Grid.Column>
                    <Grid.Column>
                      {this.updatemessage()}
                    </Grid.Column>
                  </Grid>
                </Card.Content>
              </Card> 
            </Grid.Column>
          </Grid>
        </Container>
        <Container fluid className={isMobile ? "navfooter mobile" : "navfooter"}>
          <List link horizontal>
            <List.Item as='a' className="footheader">About Us</List.Item>
            <List.Item as='a' className="footheader">Contact Us</List.Item>
            <List.Item as='a' className="footheader">Products</List.Item>
          </List>
        </Container>
      </Container>
    )
  }
}
export default Login;
