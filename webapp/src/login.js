import React from "react";
import axios from 'axios';
import { setUserSession } from './utils/common';
import { Header, Container, Button, Card, Message, Grid } from 'semantic-ui-react'
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
        this.props.history.push('/home');
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
      <Container fluid
        style={{
          marginTop: '10em',
          paddingLeft: '2em',
          paddingRight: '2em'
        }}
      >
        <Grid columns={2} doubling stackable>
          <Grid.Column textAlign="center" verticalAlign="middle">
            <Header
              content='Helping you reduce waste at home with AI solutions'
              inverted
              style={{
                color: 'black',
                fontSize: '3em',
                fontWeight: 'bold'
              }}
            />
            <Header
              content='...starting with your pantry'
              inverted
              style={{
                color: 'black',
                fontSize: '1.7em',
                fontWeight: 'normal',
                marginTop: '1.5em',
              }}
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
    )
  }
}
export default Login;
