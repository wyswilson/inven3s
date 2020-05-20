import React from "react";
import './index.css';
import { Container, Button, Card, Message, Grid } from 'semantic-ui-react'
import axios from 'axios';
import { setUserSession } from './utils/common';
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
    const { email, password } = this.state;
    this.setState({ message: 'authenticating' });
    this.setState({ tried: true });
    console.log('email:' + email)
    axios.post(this.state.apihost + '/user/login', {},
      {
       auth: {
        username: email,
        password: password
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
      return (<Card raised>
                  <Message size='tiny' warning={this.state.tried && !this.state.success}
                    header={this.state.message}
                  />
              </Card>
              )
      }
  }

  render() {
    return (
      <Container fluid>
         <Grid columns={1} doubling stackable>
          <Grid.Column>
            <Field label="email" type="text" active={false}
              parentCallback={this.updatecredentials.bind(this)}/>
          </Grid.Column>
          <Grid.Column>
            <Field label="password" type="password" active={false}
              parentCallback ={this.updatecredentials.bind(this)}/>
           </Grid.Column>
           <Grid.Row columns={2}>
            <Grid.Column>
              <Button color="grey" className="fullwidth" onClick={this.authenticate.bind(this)}>login</Button>
            </Grid.Column>
            <Grid.Column>
              {this.updatemessage()}
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Container>
    )
  }
}
export default Login;
