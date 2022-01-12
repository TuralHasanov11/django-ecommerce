let addToCartBtns = document.querySelectorAll('.update-cart')

addToCartBtns.forEach((el, key)=>{
    el.addEventListener('click', (e)=>{
        let productId = e.currentTarget.dataset.product
        let action = e.currentTarget.dataset.action
        let price = e.currentTarget.dataset.price

        if(user=='AnonymousUser'){
            [orderItems,orderTotal]=addCookieItem(productId, price, action)

            if(e.target.classList.contains('chg-quantity')){
                document.getElementById('orderItems').innerHTML=orderItems
                document.getElementById('orderTotal').innerHTML=orderTotal.toFixed(2)
                if(!cart[productId]){
                    e.target.closest('.cart-row').style.display='none'
                }else{
                    e.target.closest('.cart-row').querySelector('.item-quantity').innerHTML = cart[productId].quantity
                }
            }
            
            document.getElementById('cart-total').innerHTML=orderItems

        }else{
            updateUserOrder(productId, action)
                .then((data) =>{
                    document.getElementById('cart-total').innerHTML=data.orderItems
                    if(e.target.classList.contains('chg-quantity')){
                        document.getElementById('orderItems').innerHTML=data.orderItems
                        document.getElementById('orderTotal').innerHTML=data.orderTotal
                        if(!data.orderItemQuantity || data.orderItemQuantity<=0){
                            e.target.closest('.cart-row').style.display='none'
                        }else{
                            e.target.closest('.cart-row').querySelector('.item-quantity').innerHTML = data.orderItemQuantity
                        }
                    }
                })
        }
        
    })
})

function addCookieItem(productId, productPrice, action){

    if(action=='add'){
        if(cart[productId]==undefined){
            
            cart[productId]={quantity:1, price:productPrice}
        }else{
            cart[productId].quantity+=1
        }
    }else if(action=='remove'){
        cart[productId].quantity-=1

        if(cart[productId].quantity<=0){
            delete cart[productId]
        }
    }

    [orderItems,orderTotal]=getCartData()
    
    document.cookie = 'cart='+JSON.stringify(cart)+";domain=;path=/"

    return [orderItems, orderTotal]
}


async function updateUserOrder(productId, action){
    var url = '/update-item/'

    const response = await fetch(url,{
                        method:'POST',
                        headers:{
                            'Content-Type':'application/json',
                            'X-CSRFToken':csrftoken
                        },
                        body:JSON.stringify({
                            'productId':productId,
                            'action':action
                        })
                    })

    return response.json()
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
var cart = JSON.parse(getCookie('cart'));

function getCartData(){
    let orderItems = 0
    let orderTotal = 0

    for (const item in cart) {
        orderItems+=cart[item].quantity
        orderTotal += cart[item].quantity*cart[item].price
    }

    return [orderItems, orderTotal]
}

if(cart==undefined){
    cart = {}
    document.cookie = 'cart='+JSON.stringify(cart)+";path=/"
}