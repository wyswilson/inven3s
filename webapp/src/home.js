import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken, getUser, removeUserSession } from './utils/common';
import { Image, Header, Feed, Card, Message, Grid, Button, Statistic } from 'semantic-ui-react'
import _ from 'lodash'

class Home extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      //apihost: 'http://127.0.0.1:88',
      apihost: 'https://inven3s.xyz',
      username: getUser(),
      token: getToken(),
      insightsloaded: false,
      itemcnt : {
        ediblenewcnt: 0,
        edibleopenedcnt: 0,
        inediblenewcnt: 0,
        inedibleopenedcnt: 0,
        expiredcnt: 0,
        expiringcnt: 0,
        shoppinglistcnt: 0,
      },
      feed: <Feed></Feed>
    };
  }

  handlelogout(e) {
    removeUserSession();
    this.props.history.push('/login');
  }

  redirectoproduct(gtin, productname, productimage, productimagelocal, brandname, isedible, isfavourite, categories){
    this.props.history.push({
      pathname: '/product',
      state: { gtin: gtin, productname: productname, productimage: productimage, productimagelocal: productimagelocal, brandname: brandname, isedible: isedible, isfavourite: isfavourite, categoryoptions: categories }
    })
  }

  formatactivityfeed(activities){
    const feed = _.map(activities, (item) => (
        <Feed.Event key={ item.gtin + (new Date().getTime()) }>
          <Feed.Label alt={item.productname}>
            <Image
              wrapped src={item.productimagelocal} size='tiny'
              onError={(e)=>{e.target.onerror = null; e.target.src=item.productimage}}
            />
          </Feed.Label>
          <Feed.Content>
            <Feed.Summary>
              {item.itemstatus === 'IN' ? 'added ' : 'consumed '}
              <Feed.User onClick={this.redirectoproduct.bind(this,item.gtin,item.productname, item.productimage, item.productimagelocal, item.brandname, item.isedible, item.isfavourite, item.categories)}>{item.productname}</Feed.User>
              {item.itemstatus === 'IN' ? ' (' + item.itemcount + ' items)' : ''}
              <Feed.Date>{item.dateentry}</Feed.Date>
            </Feed.Summary>
            <Feed.Meta></Feed.Meta>
          </Feed.Content>
        </Feed.Event>
      )
    );

    this.setState( { feed: feed});
  }

  getinventoryfeed(){
    console.log('getinventoryfeed');

    axios.get(this.state.apihost + '/inventory/feed',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        console.log('getinventoryfeed [' + response.data[0]['message'] + ']');

        this.formatactivityfeed( response.data[0]['results'] );
        this.getinventorycount();
      }
    })
    .catch(error => {
      if(error.response){
        console.log("getinventoryfeed ["+ error.response.status + ":" + error.response.data[0]['message'] + ']');
      }
      else{
        console.log('getinventoryfeed [server unreachable]');
      }
    });
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
        const shoppinglistcnt = response.data[0]['counts']['shoppinglist'];

        this.setState({expiringcnt: expiringcnt});
        this.setState({expiredcnt: expiredcnt});
        this.setState({ediblenewcnt: ediblenewcnt});
        this.setState({edibleopenedcnt: edibleopenedcnt});
        this.setState({inediblenewcnt: inediblenewcnt});
        this.setState({inedibleopenedcnt: inedibleopenedcnt});
        this.setState({shoppinglistcnt: shoppinglistcnt});

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
    if(isedible >= 0 && isopened >= 0){
      this.props.history.push({
        pathname: '/pan3',
        //search: '?isedible=' + isedible + '&isopened=' + isopened,
        state: { queryisedible: isedible, queryisopened: isopened, queryexpirystatus: expirystatus }
      })      
    }
    else{
      this.props.history.push({
        pathname: '/2buy'
      }) 
    }

  }

  componentDidMount() {
    this.getinventoryfeed();
  }

  generateinsights(){
    const stats = [
     {
        'id':1,
        'number': this.state.shoppinglistcnt,
        'label': 'items in 2Buy',
        'isedible':-1,'isopened':-1,'expirystatus':'all'
      },
      {
        'id':2,
        'number': this.state.expiringcnt,
        'label': 'expiring food items',
        'isedible':2,'isopened':2,'expirystatus':'expiring'
      },
      {
        'id':3,
        'number': this.state.expiredcnt,
        'label': 'expired food items',
        'isedible':2,'isopened':2,'expirystatus':'expired'
      },
      {
        'id':4,
        'number': this.state.edibleopenedcnt,
        'label': 'opened food items',
        'isedible':1,'isopened':1,'expirystatus':'all'
      },
      {
        'id':5,
        'number': this.state.ediblenewcnt,
        'label': 'new food items',
        'isedible':1,'isopened':0,'expirystatus':'all'
      },
      {
        'id':6,
        'number': this.state.inedibleopenedcnt,
        'label': 'opened non-food items',
        'isedible':0,'isopened':1,'expirystatus':'all'
      },
      {
        'id':7,
        'number': this.state.inediblenewcnt,
        'label': 'new non-food items',
        'isedible':0,'isopened':0,'expirystatus':'all'
      }
    ];

    if(this.state.insightsloaded){
      return stats.map( (stat) => (
              <Grid.Column key={stat.id} textAlign="center">
                <Card raised key={stat.id} fluid onClick={this.directtoinventory.bind(this,stat.isedible,stat.isopened,stat.expirystatus)}>
                  <Card.Content>
                    <Statistic size="tiny">
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
              <Message size='tiny'
                header="Generating insights for you"
                content="Please try again later if it doesn't load"
              />
            </Grid.Column>
          );
    }
  }

  render() {
    return (
      <div
        className={isMobile ? "bodymain mobile" : "bodymain"}
      >
         <Grid columns={2} doubling stackable>
          <Grid.Column textAlign="left">
            <Grid columns={2} doubling stackable textAlign='left'>
              <Grid.Column key={0} textAlign="center">
                <Card raised key={0} fluid>
                  <Card.Content textAlign='center'>
                    <Header size='small'>{this.state.username}'s pantry</Header>
                    <Button className='kuning button' onClick={this.handlelogout.bind(this)}>LOGOUT</Button>
                  </Card.Content>
                </Card> 
              </Grid.Column>
              {this.generateinsights()}
            </Grid>
          </Grid.Column>
          <Grid.Column textAlign="left">   
            <Feed>  
              <Header size='small'>Pantry activities</Header>
              {this.state.feed}    
            </Feed>
          </Grid.Column>
        </Grid>
      </div>
    )
  }
}
export default Home;

