import React, {Fragment} from "react";
import "./index.css";
import { Search } from 'semantic-ui-react'
import axios from 'axios';
import { getToken } from './utils/common';
import PropTypes from 'prop-types'
import _ from 'lodash'
import { Button, Icon, Label, Card, Image  } from 'semantic-ui-react'

const cards = [
  {
    avatar: '/images/avatar/large/helen.jpg',
    date: 'Joined in 2013',
    header: 'Helen',
    description: 'Primary Contact',
  },
  {
    avatar: '/images/avatar/large/matthew.png',
    date: 'Joined in 2013',
    header: 'Matthew',
    description: 'Primary Contact',
  },
  {
    avatar: '/images/avatar/large/molly.png',
    date: 'Joined in 2013',
    header: 'Molly',
    description: 'Primary Contact',
  },
  {
    avatar: '/images/avatar/large/molly.png',
    date: 'Joined in 2013',
    header: 'Theia',
    description: 'Primary Contact',
  }
]


const renderproducts = ({ gtin, productname }) => (
  <div>
  {productname}
  </div>
)

renderproducts.propTypes = {
  gtin: PropTypes.string,
  productname: PropTypes.string,
}

const renderretailers = ({ retailername }) => (
  <div>
  {retailername}
  </div>
)

renderretailers.propTypes = {
  retailername: PropTypes.string
}

const defaultproduct = [{
          "key":"",
          "title":"",
          "gtin": "new-entry",
          "productname": "create new entry",
          "productimage": "",
          "brandname": "",
          "isperishable": 0,
          "isedible": 1
        }]

const defaultretailer = [{
          "key":"",
          "title":"",
          "retailerid": "new-entry",
          "retailername": "create new entry"
        }]

class Inventory extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      token: getToken(),
      gtin: '',
      productname: '',
      retailerid:'',
      retailername:'',
      inventory:[],
      productsuggests: defaultproduct,
      retailersuggests: defaultretailer
    }
  }

  componentDidMount() {
    const { token } = this.state;
    
    if (!token) {
      return;
    }

    axios.get('http://127.0.0.1:8989/inventory',
      { headers: { "content-type": "application/json", "access-token": token } }
    )
    .then(response => { 
      if(response.status === 200){
        const inventoryitems = response.data[0]['results'];
        this.setState({ inventory:inventoryitems });
        console.log(inventoryitems);
      }
    })
    .catch(error => {
      const errresponse = error.response
      if(errresponse){
        if(errresponse.status === 412){
          const message = errresponse.data[0]['message'];
          console.log(message);
        }
        else{
          console.log(errresponse);
        }
      }
      else{
        console.log('internal server error');
      }
    });
  }

  lookupretailer(retailer){
    const { token } = this.state;

    if(retailer.length > 3){
      axios.get('http://127.0.0.1:8989/retailer/' + retailer,
        { headers: { "content-type": "application/json", "access-token": token } }
      )
      .then(response => { 
        if(response.status === 200){
          const suggestions = response.data[0]['results'];
          this.setState({ retailersuggests:suggestions });
          console.log(suggestions);
        }
      })
      .catch(error => {
        const errresponse = error.response
        if(errresponse){
          if(errresponse.status === 412){
            const message = errresponse.data[0]['message'];
            console.log(message);
          }
          else{
            console.log(errresponse);
          }
        }
        else{
          console.log('internal server error');
        }
      });
    }
  }
  lookupproduct(gtinorproduct){
    const { token } = this.state;

    if(gtinorproduct.length > 3){
      axios.get('http://127.0.0.1:8989/product/' + gtinorproduct,
        { headers: { "content-type": "application/json", "access-token": token } }
      )
      .then(response => { 
        if(response.status === 200){
          const suggestions = response.data[0]['results'];
          this.setState({ productsuggests:suggestions });
          console.log(suggestions);
        }
      })
      .catch(error => {
        const errresponse = error.response
        if(errresponse){
          if(errresponse.status === 412){
            const message = errresponse.data[0]['message'];
            console.log(message);
          }
          else{
            console.log(errresponse);
          }
        }
        else{
          console.log('internal server error');
        }
      });
    }
  }
  updateinventory(field,value) {
    console.log('parent:'+field + ':' + value);

    if(field === 'gtin'){
      this.lookupproduct(value);
    }
    else if(field === 'retailer'){

    }
  }
  updateproductsuggests(event){
    const gtin = event.target.value;
    this.lookupproduct(gtin);
  }
  updateretailersuggests(event){
    const retailername = event.target.value;
    this.lookupretailer(retailername);
  }
  selectproduct(event, { result }){
    if(result.gtin !== 'new-entry'){
      console.log("selected=>" + result.gtin + ":" + result.productname);
      this.setState({ gtin: result.gtin, productname: result.productname });
    }
    else{
      console.log('new-entry');
    }
  }
  selectretailer(event, { result }){
    if(result.retailerid !== 'new-entry'){
      console.log("selected=>" + result.retailerid + ":" + result.retailername);
      this.setState({ retailerid: result.retailerid, retailername: result.retailername });
    }
    else{
      console.log('new-entry');
    }
  }

  render() {
    const { token, gtin, productname, retailerid, retailername, productsuggests, retailersuggests, inventory } = this.state;
    const itemgrid = _.map(inventory, (item) => (
            <Card raised key={item.gtin}>
              <Image rounded centered src={item.productimage} size="tiny"/>
              <Card.Content>
                <Label color='grey' ribbon>{item.itemcount}</Label>
                <Fragment>
                  <Card.Header className="cardy">{item.productname}</Card.Header>
                  <Card.Meta>{item.brandname}</Card.Meta>
                </Fragment>
              </Card.Content>

              <Card.Content extra textAlign="center">
                <Button icon="minus" />
                <Button icon="plus" />
              </Card.Content>
            </Card>
          ))
    return (
      <div>
         <Search className="searchsuggest"
          fluid
          icon="search"
          placeholder="product name or gtin"
          resultRenderer={renderproducts}
          results={productsuggests}
          onSearchChange={this.updateproductsuggests.bind(this)}
          onResultSelect={this.selectproduct.bind(this)}
          size="small"
        />
        <Search className="searchsuggest"
          fluid
          icon="search"
          placeholder="retailer"
          resultRenderer={renderretailers}
          results={retailersuggests}
          onSearchChange={this.updateretailersuggests.bind(this)}
          onResultSelect={this.selectretailer.bind(this)}
          size="small"
        />

        <Card.Group doubling itemsPerRow={6} stackable>
            {itemgrid}
        </Card.Group>
      </div>
    )
  }
}
export default Inventory;
