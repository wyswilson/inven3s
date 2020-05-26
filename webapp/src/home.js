import React from "react";
import axios from 'axios';
import { getToken, getUser, removeUserSession } from './utils/common';
import { Card, Message, Container, Grid, Button, Statistic } from 'semantic-ui-react'

class Home extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      apihost: 'http://13.229.67.229:8989',
      username: getUser(),
      token: getToken(),
      insightsloaded: false,
      itemcnt : {
        ediblenewcnt: 0,
        edibleopenedcnt: 0,
        inediblenewcnt: 0,
        inedibleopenedcnt: 0,
        expiredcnt: 0,
        expiringcnt: 0
      }
    };
  }

  handlelogout(e) {
    removeUserSession();
    this.props.history.push('/login');
  }

  getinventorycount(){
    console.log('getinventorycount');

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
        console.log('getinventorycount [' + response.data[0]['message'] + ']');

        const ediblenewcnt = response.data[0]['counts']['ediblenew'];
        const edibleopenedcnt = response.data[0]['counts']['edibleopened'];
        const inediblenewcnt = response.data[0]['counts']['inediblenew'];
        const inedibleopenedcnt = response.data[0]['counts']['inedibleopened'];
        const expiringcnt = response.data[0]['counts']['expiring'];
        const expiredcnt = response.data[0]['counts']['expired'];

        this.setState({expiringcnt: expiringcnt});
        this.setState({expiredcnt: expiredcnt});
        this.setState({ediblenewcnt: ediblenewcnt});
        this.setState({edibleopenedcnt: edibleopenedcnt});
        this.setState({inediblenewcnt: inediblenewcnt});
        this.setState({inedibleopenedcnt: inedibleopenedcnt});

        this.setState({insightsloaded: true});
      }
    })
    .catch(error => {
      if(error.response){
        console.log("getinventorycount ["+ error.response.status + ":" + error.response.data[0]['message'] + ']');
      }
      else{
        console.log('getinventorycount [server unreachable]');
      }
    });
  }

  directtoinventory(isedible,isopened,expirystatus){
    this.props.history.push({
      pathname: '/inventory',
      //search: '?isedible=' + isedible + '&isopened=' + isopened,
      state: { queryisedible: isedible, queryisopened: isopened, queryexpirystatus: expirystatus }
    })
  }

  componentDidMount() {
    this.getinventorycount();
  }

  generateinsights(){
    const stats = [
      {
        'number': this.state.edibleopenedcnt,
        'label': '# of opened food items',
        'isedible':1,'isopened':1,'expirystatus':'all'
      },
      {
        'number': this.state.ediblenewcnt,
        'label': '# of new food items',
        'isedible':1,'isopened':0,'expirystatus':'all'
      },
      {
        'number': this.state.expiringcnt,
        'label': '# of expiring food items',
        'isedible':2,'isopened':2,'expirystatus':'expiring'
      },
      {
        'number': this.state.expiredcnt,
        'label': '# of expired food items',
        'isedible':2,'isopened':2,'expirystatus':'expired'
      },
      {
        'number': this.state.inedibleopenedcnt,
        'label': '# of opened non-food items',
        'isedible':0,'isopened':1,'expirystatus':'all'
      },
      {
        'number': this.state.inediblenewcnt,
        'label': '# of new non-food items',
        'isedible':0,'isopened':0,'expirystatus':'all'
      }
    ];

    if(this.state.insightsloaded){
      return stats.map( (stat) => (
              <Grid.Column textAlign="center">
                <Card raised key="1" fluid onClick={this.directtoinventory.bind(this,stat.isedible,stat.isopened,stat.expirystatus)}>
                  <Card.Content>
                    <Statistic size="small">
                      <Statistic.Value>
                      {stat.number}</Statistic.Value>
                      <Statistic.Label>{stat.label}</Statistic.Label>
                    </Statistic>
                  </Card.Content>
                </Card> 
              </Grid.Column>
          ));
    }
    else{
      return (
            <Grid.Column textAlign="center">
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
      <Container textAlign="left" fluid>
         <Grid columns={5} doubling stackable>
          <Grid.Column textAlign="center">
            <Card raised key="1" fluid>
              <Card.Content>
                <Card.Header>{this.state.username}'s inventory</Card.Header>
              </Card.Content>
              <Card.Content extra>
                <Button color="grey" onClick={this.handlelogout.bind(this)}>
                Logout</Button>
              </Card.Content>
            </Card> 
          </Grid.Column>
          {this.generateinsights()}
        </Grid>
      </Container>
    )
  }
}
export default Home;

