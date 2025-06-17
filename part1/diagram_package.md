@startuml
!theme cerulean-outline
title Three layer architecture of the HBnB project

package "Presentation Layer" {
    [API Services] as apiGateway
    [UserAPI]
    [PlaceAPI]
    [ReviewAPI]
    [AmenityAPI]
}

package "Business Logic Layer" {
    [Facade] as facade
    [Base Model] as baseModel
    [User Model] as userModel
    [Place Model] as placeModel
    [Review Model] as reviewModel
    [Amenity Model] as amenityModel
}

package "Persistence Layer" {
    [UserRepository] as userRepo
    [PlaceRepository] as placeRepo
    [ReviewRepository] as reviewRepo
    [AmenityRepository] as amenityRepo
    [Database] as database
}

' Connexions entre les composants
apiGateway <--> UserAPI : Transfer to
apiGateway <--> PlaceAPI : Transfer to
apiGateway <--> ReviewAPI : Transfer to
apiGateway <--> AmenityAPI : Transfer to

UserAPI <--> facade : Delegates to
PlaceAPI <--> facade : Delegates to
ReviewAPI <--> facade : Delegates to
AmenityAPI <--> facade : Delegates to

userModel -[#green]|> baseModel
placeModel -[#green]|> baseModel
reviewModel -[#green]|> baseModel : <color:green>inherited
amenityModel -[#green]|> baseModel : <color:green>inherited


facade <--> userModel : Used
facade <--> placeModel : Used
facade <--> reviewModel : Used
facade <--> amenityModel : Used

userModel <--> userRepo : accesses
placeModel <--> placeRepo : accesses
reviewModel <--> reviewRepo : accesses
amenityModel <--> amenityRepo : accesses

userRepo <--> database : Request SQL
placeRepo <--> database : Request SQL
reviewRepo <--> database : Request SQL
amenityRepo <--> database : Request SQL
@enduml
