import React from "react";
import "./index.css";
import axios from 'axios';
import { getToken, getUser, removeUserSession } from './utils/common';
import { Message, Header, Container, Grid, Button, Statistic } from 'semantic-ui-react'

class Insights extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      apihost: 'http://127.0.0.1:8989',
      username: getUser(),
      token: getToken(),
      insightsloaded: false,
      itemcnt : {
        ediblenewcnt: 0,
        edibleopenedcnt: 0,
        inediblenewcnt: 0,
        inedibleopenedcnt: 0
      }
    };
  }

  handlelogout(e) {
    removeUserSession();
    this.props.history.push('/login');
  }

  getinventorycount(){
    axios.get(this.state.apihost + '/inventory/insights',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        const ediblenewcnt = response.data[0]['counts']['ediblenew'];
        const edibleopenedcnt = response.data[0]['counts']['edibleopened'];
        const inediblenewcnt = response.data[0]['counts']['inediblenew'];
        const inedibleopenedcnt = response.data[0]['counts']['inedibleopened'];

        this.setState({ediblenewcnt: ediblenewcnt});
        this.setState({edibleopenedcnt: edibleopenedcnt});
        this.setState({inediblenewcnt: inediblenewcnt});
        this.setState({inedibleopenedcnt: inedibleopenedcnt});

        this.setState({insightsloaded: true});
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

  directtoinventory(isedible,ispartiallyconsumed){
    this.props.history.push({
      pathname: '/inventory',
      state: { queryisedible: isedible, queryispartiallyconsumed: ispartiallyconsumed }
    })
  }

  componentDidMount() {
    this.getinventorycount();
  }

  generateinsights(){
    if(this.state.insightsloaded){
      return (
            <Grid.Row columns={4}>
              <Grid.Column>
                <Statistic>
                  <Statistic.Value onClick={this.directtoinventory.bind(this,1,1)}>{this.state.edibleopenedcnt}</Statistic.Value>
                  <Statistic.Label># of opened food items</Statistic.Label>
                </Statistic>
              </Grid.Column>
              <Grid.Column>
                <Statistic>
                  <Statistic.Value onClick={this.directtoinventory.bind(this,1,0)}>{this.state.ediblenewcnt}</Statistic.Value>
                  <Statistic.Label># of new food items</Statistic.Label>
                </Statistic>            
              </Grid.Column>
              <Grid.Column>
                <Statistic>
                  <Statistic.Value onClick={this.directtoinventory.bind(this,0,1)}>{this.state.inedibleopenedcnt}</Statistic.Value>
                  <Statistic.Label># of opened non-food items</Statistic.Label>
                </Statistic>
              </Grid.Column>
              <Grid.Column>
                <Statistic>
                  <Statistic.Value onClick={this.directtoinventory.bind(this,0,0)}>{this.state.inediblenewcnt}</Statistic.Value>
                  <Statistic.Label># of new non-food items</Statistic.Label>
                </Statistic>            
              </Grid.Column>
            </Grid.Row>
          )
    }
    else{
      return (
            <Grid.Column>
              <Message warning size='tiny'
                header="Problem generating insights"
                content="Please try again later if it doesn't load"
              />
            </Grid.Column>
          )
    }
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
          {this.generateinsights()}
        </Grid>
      </Container>
    )
  }
}
export default Insights;

