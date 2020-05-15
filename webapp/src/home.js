import React from "react";
import "./index.css";
import axios from 'axios';
import { getToken, getUser, removeUserSession } from './utils/common';
import { Header, Container, Grid, Button, Statistic } from 'semantic-ui-react'

class Insights extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      username: getUser(),
      token: getToken(),
      itemcnt : {
        distinctedible: 0
      }
    };
  }

  handlelogout(e) {
    removeUserSession();
    this.props.history.push('/login');
  }

  getinventorycount(){
    axios.get('http://127.0.0.1:8989/inventory?isedible=1&ispartiallyconsumed=2&sortby=productname',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        const distinctedible = response.data[0]['count'];
        this.setState({distinctedible: distinctedible});
      }
    })
    .catch(error => {
      if(error.response){
        console.log("("+ error.response.status + ") " + error.response.data[0]['message']);
      }
      else{
        console.log('fatal: server unreachable');
      }
    });
  }

  componentDidMount() {
    this.getinventorycount();
  }

  render() {
    return (
      <Container fluid>
         <Grid columns={1} doubling stackable>
          <Grid.Column>
            <Header as='h1'>
              Welcome to inventory for {this.state.username}
            </Header>
            <Button color="black" onClick={this.handlelogout.bind(this)}>logout</Button>
          </Grid.Column>
          <Grid.Row columns={3}>
            <Grid.Column>
              <Statistic>
                <Statistic.Value>{this.state.distinctedible}</Statistic.Value>
                <Statistic.Label>Edible Items</Statistic.Label>
              </Statistic>
            </Grid.Column>
            <Grid.Column>
              <Statistic>
                <Statistic.Value>{this.state.distinctedible}</Statistic.Value>
                <Statistic.Label>Edible Items</Statistic.Label>
              </Statistic>            
            </Grid.Column>
            <Grid.Column>
              <Statistic>
                <Statistic.Value>{this.state.distinctedible}</Statistic.Value>
                <Statistic.Label>Edible Items</Statistic.Label>
              </Statistic>            
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Container>
    )
  }
}
export default Insights;

