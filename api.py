from flask_restful import Api, Resource, reqparse
from main import app, SellCar, db

api = Api(app)


class SellCarResource(Resource):
    def get(self, id=None):
        if id:
            post = SellCar.query.get(id)
            if post:
                return {
                    'id': post.id,
                    'firstName': post.firstName,
                    'phone': post.phone,
                    'photo': post.photo,
                    'email': post.email,
                    'description': post.description,
                    'price': post.price,
                    'date': post.date.isoformat(),
                }
            else:
                return {'error': 'Post not found'}, 404
        else:
            posts = SellCar.query.order_by(SellCar.date.desc()).all()
            serialized_posts = [{
                'id': post.id,
                'firstName': post.firstName,
                'phone': post.phone,
                'photo': post.photo,
                'email': post.email,
                'description': post.description,
                'price': post.price,
                'date': post.date.isoformat(),
            } for post in posts]
            return {'posts': serialized_posts}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('firstName', type=str, required=True)
        parser.add_argument('phone', type=str, required=True)
        parser.add_argument('photo', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('price', type=int, required=True)

        args = parser.parse_args()

        sell_car = SellCar(
            firstName=args['firstName'],
            phone=args['phone'],
            photo=args['photo'],
            email=args['email'],
            description=args['description'],
            price=args['price']
        )

        try:
            db.session.add(sell_car)
            db.session.commit()
            return {'message': 'Post created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': f"An error occurred while adding: {str(e)}"}, 500

    def delete(self, id):
        post = SellCar.query.get_or_404(id)

        try:
            db.session.delete(post)
            db.session.commit()
            return {'message': 'Post deleted successfully'}, 200
        except Exception as e:
            return {'error': f"An error occurred while deleting a post: {str(e)}"}, 500

    def put(self, id):
        post = SellCar.query.get_or_404(id)

        parser = reqparse.RequestParser()
        parser.add_argument('firstName', type=str, required=True)
        parser.add_argument('phone', type=str, required=True)
        parser.add_argument('photo', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('price', type=int, required=True)

        args = parser.parse_args()

        post.firstName = args['firstName']
        post.phone = args['phone']
        post.photo = args['photo']
        post.email = args['email']
        post.description = args['description']
        post.price = args['price']

        try:
            db.session.commit()
            return {'message': 'Post updated successfully'}, 200
        except Exception as e:
            return {'error': f"An error occurred while updating a post: {str(e)}"}, 500


api.add_resource(SellCarResource, '/api/posts', '/api/posts/<int:id>')
